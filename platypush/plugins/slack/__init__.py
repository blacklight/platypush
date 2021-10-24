import json
from typing import Optional, Iterable

import multiprocessing
import requests
from websocket import WebSocketApp

from platypush.context import get_bus
from platypush.message.event.chat.slack import SlackMessageReceivedEvent, SlackMessageDeletedEvent, \
    SlackMessageEditedEvent, SlackAppMentionReceivedEvent
from platypush.plugins import RunnablePlugin, action
from platypush.plugins.chat import ChatPlugin


class SlackPlugin(ChatPlugin, RunnablePlugin):
    """
    Plugin used to interact with Slack instances.

    You'll have to generate your own Slack app and tokens in order to use this plugin. Steps:

        - Create a new Slack app `here <https://api.slack.com/apps>` and associate a Slack workspace to it.
        - In the configuration panel of your app scroll to Socket Mode and select Enable Socket Mode.
        - Scroll to Event Subscriptions and select Enable Events.
        - Choose the type of events that you want to subscribe to. You can select bot events (i.e. when somebody in
          the channel mentions the name of your app) or any of the workspace events (e.g. creation of messages, user
          events etc.).
        - Scroll to App-Level Tokens and generate a new token with ``connections:write`` scope. This token will be
          used to receive Slack events over websocket.
        - Scroll to OAuth & Permissions and select the scopes that you want to enable. You may usually want to enable
          Bot Token Scopes -> ``app_mentions:read``, so the script can react when somebody mentions its name. You may
          also want to select the user scopes relevant to your application - e.g. read/write messages, manage users etc.
        - If you changed scopes and settings, you may have to reinstall the app in the workspace through the
          Install App menu.
        - Navigate to the Install App menu. If the app has been correctly installed in your workspace then you should
          see a Bot User OAuth Token, used to authenticate API calls performed as the app/bot. If you also granted
          user permissions to the app then you should also see a User OAuth Token on the page.

    Triggers:

        - :class:`platypush.message.event.chat.slack.SlackMessageReceivedEvent` when a message is received on a
            monitored channel.
        - :class:`platypush.message.event.chat.slack.SlackMessageEditedEvent` when a message is edited on a
            monitored channel.
        - :class:`platypush.message.event.chat.slack.SlackMessageDeletedEvent` when a message is deleted from a
            monitored channel.
        - :class:`platypush.message.event.chat.slack.SlackAppMentionReceivedEvent` when a message that mentions
            the app is received on a monitored channel.

    """

    _api_base_url = 'https://slack.com/api'

    def __init__(self, app_token: str, bot_token: str, user_token: Optional[str] = None, **kwargs):
        """
        :param app_token: Your Slack app token.
        :param bot_token: Bot OAuth token reported on the *Install App* menu.
        :param user_token: User OAuth token reported on the *Install App* menu.
        """
        super().__init__(**kwargs)
        self._app_token = app_token
        self._bot_token = bot_token
        self._user_token = user_token
        self._ws_url: Optional[str] = None
        self._ws_app: Optional[WebSocketApp] = None
        self._ws_listener: Optional[multiprocessing.Process] = None
        self._connected_event = multiprocessing.Event()
        self._disconnected_event = multiprocessing.Event()
        self._state_lock = multiprocessing.RLock()

    @classmethod
    def _url_for(cls, method: str) -> str:
        return f'{cls._api_base_url}/{method}'

    @action
    def send_message(self, channel: str, as_user: bool = False, text: Optional[str] = None,
                     blocks: Optional[Iterable[str]] = None, **kwargs):
        """
        Send a message to a channel.
        It requires a token with ``chat:write`` bot/user scope.

        :param channel: Channel ID or name.
        :param as_user: If true then the message will be sent as the authorized user, otherwise as the application bot
            (default: false).
        :param text: Text to be sent.
        :param blocks: Extra blocks to be added to the message (e.g. images, links, markdown). See
            `Slack documentation for blocks <https://api.slack.com/reference/block-kit/blocks>`_.
        """
        rs = requests.post(
            self._url_for('chat.postMessage'),
            headers={
                'Authorization': f'Bearer {self._user_token if as_user else self._bot_token}'
            },
            json={
                'channel': channel,
                'text': text,
                'blocks': blocks or [],
            }
        )

        try:
            rs.raise_for_status()
            rs = rs.json()
            assert rs.get('ok'), rs.get('error', rs.get('warning'))
        except Exception as e:
            raise AssertionError(e)

    def main(self):
        self._connect()
        stop_events = []

        while not any(stop_events):
            stop_events = self._should_stop.wait(timeout=1), self._disconnected_event.wait(timeout=1)

    def stop(self):
        if self._ws_app:
            self._ws_app.close()
            self._ws_app = None

        if self._ws_listener and self._ws_listener.is_alive():
            self.logger.info('Terminating websocket process')
            self._ws_listener.terminate()
            self._ws_listener.join(5)

        if self._ws_listener and self._ws_listener.is_alive():
            self.logger.warning('Terminating the websocket process failed, killing the process')
            self._ws_listener.kill()

        if self._ws_listener:
            self._ws_listener.join()
            self._ws_listener = None

        super().stop()

    def _connect(self):
        with self._state_lock:
            if self.should_stop() or self._connected_event.is_set():
                return

            self._ws_url = None
            rs = requests.post('https://slack.com/api/apps.connections.open', headers={
                'Authorization': f'Bearer {self._app_token}',
            })

            try:
                rs.raise_for_status()
            except:   # lgtm [py/catch-base-exception]
                if rs.status_code == 401 or rs.status_code == 403:
                    self.logger.error('Unauthorized/Forbidden Slack API request, stopping the service')
                    self.stop()
                    return

                raise

            rs = rs.json()
            assert rs.get('ok')
            self._ws_url = rs.get('url')
            self._ws_app = WebSocketApp(self._ws_url,
                                        on_open=self._on_open(),
                                        on_message=self._on_msg(),
                                        on_error=self._on_error(),
                                        on_close=self._on_close())

            def server():
                self._ws_app.run_forever()

            self._ws_listener = multiprocessing.Process(target=server)
            self._ws_listener.start()

    def _on_open(self):
        def hndl(*_):
            with self._state_lock:
                self._disconnected_event.clear()
                self._connected_event.set()
            self.logger.info('Connected to the Slack websocket')

        return hndl

    @staticmethod
    def _send_ack(ws: WebSocketApp, msg):
        envelope_id = msg.get('envelope_id')
        if envelope_id:
            # Send ACK
            ws.send(json.dumps({
                'envelope_id': envelope_id,
            }))

    def _on_msg(self):
        def hndl(*args):
            ws = args[0] if len(args) > 1 else self._ws_app
            data = json.loads(args[1] if len(args) > 1 else args[0])
            output_event = None
            self._send_ack(ws, data)

            if data['type'] == 'events_api':
                event = data.get('payload', {}).get('event', {})
                event_args = {}

                if event['type'] == 'app_mention':
                    output_event = SlackAppMentionReceivedEvent(
                        text=event['text'],
                        user=event['user'],
                        channel=event['channel'],
                        team=event['team'],
                        timestamp=event['event_ts'],
                        icons=event.get('icons'),
                        blocks=event.get('blocks')
                    )
                elif event['type'] == 'message':
                    msg = event.copy()
                    prev_msg = event.get('previous_message')
                    event_type = SlackMessageReceivedEvent

                    if event.get('subtype') == 'message_deleted':
                        msg = prev_msg
                        event_type = SlackMessageDeletedEvent
                        event_args['timestamp'] = event['deleted_ts']
                    else:
                        event_args['timestamp'] = msg.get('ts')
                        if event.get('subtype') == 'message_changed':
                            msg = msg.get('message', msg)
                            event_args['previous_message'] = prev_msg
                            event_type = SlackMessageEditedEvent

                    event_args.update({
                        'text': msg.get('text'),
                        'user': msg.get('user'),
                        'channel': msg.get('channel', event.get('channel')),
                        'team': msg.get('team'),
                        'icons': msg.get('icons'),
                        'blocks': msg.get('blocks'),
                    })

                    output_event = event_type(**event_args)

            if output_event:
                get_bus().post(output_event)

        return hndl

    def _on_error(self):
        def hndl(*args):
            error = args[1] if len(args) > 1 else args[0]
            ws = args[0] if len(args) > 1 else None
            self.logger.warning('Slack websocket error: {}'.format(error))
            if ws:
                ws.close()

        return hndl

    def _on_close(self):
        def hndl(*_):
            with self._state_lock:
                self._disconnected_event.set()
                self._connected_event.clear()
            self.logger.warning('Slack websocket connection closed')

        return hndl
