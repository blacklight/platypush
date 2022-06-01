import asyncio
import json
import multiprocessing
import os
import time
from typing import Optional, Collection, Mapping

import requests
import websockets

from platypush.context import get_bus
from platypush.message.event.ntfy import NotificationEvent
from platypush.plugins import RunnablePlugin, action
from platypush.context import get_or_create_event_loop


class NtfyPlugin(RunnablePlugin):
    """
    Ntfy integration.

    `ntfy <https://ntfy.sh/>`_ allows you to process asynchronous notification
    across multiple devices and it's compatible with the
    `UnifiedPush <https://unifiedpush.org/>` specification.

    Triggers:

        * :class:`platypush.message.event.ntfy.NotificationEvent` when a new notification is received.

    """

    def __init__(
        self,
        server_url: str = 'https://ntfy.sh',
        subscriptions: Optional[Collection[str]] = None,
        **kwargs,
    ):
        """
        :param server_url: Default ntfy instance base URL (default: ``https://ntfy.sh``).
        :param subscriptions: List of topics the plugin should subscribe to
            (default: none).
        """
        super().__init__(**kwargs)
        self._server_url = server_url
        self._ws_url = '/'.join(
            [
                self._server_url.split('/')[0].replace('http', 'ws'),
                *self._server_url.split('/')[1:],
            ]
        )

        self._event_loop: Optional[asyncio.AbstractEventLoop] = None
        self._subscriptions = subscriptions or []
        self._ws_proc = None

    def _connect(self):
        if self.should_stop():
            self.logger.debug('Already connected')
            return

        self._ws_proc = multiprocessing.Process(target=self._ws_process)
        self._ws_proc.start()

        while not self._should_stop.is_set():
            self._should_stop.wait(timeout=1)

    async def _get_ws_handler(self, url):
        reconnect_wait_secs = 1
        reconnect_wait_secs_max = 60

        while True:
            self.logger.debug(f'Connecting to {url}')

            try:
                async with websockets.connect(url) as ws:
                    reconnect_wait_secs = 1
                    self.logger.info(f'Connected to {url}')
                    async for msg in ws:
                        try:
                            msg = json.loads(msg)
                        except json.JSONDecodeError as e:
                            self.logger.warning(
                                'Received invalid JSON message from the server: %s\n%s',
                                e,
                                msg,
                            )
                            continue

                        self.logger.debug('Received message on ntfy: %s', msg)
                        if msg.get('event') == 'message':
                            get_bus().post(
                                NotificationEvent(
                                    id=msg['id'],
                                    time=msg['time'],
                                    topic=msg['topic'],
                                    message=msg.get('message'),
                                    title=msg.get('title'),
                                    tags=msg.get('tags'),
                                    click_url=msg.get('click'),
                                    actions=msg.get('actions'),
                                    attachment=msg.get('attachment'),
                                )
                            )
            except websockets.exceptions.WebSocketException as e:
                self.logger.error('Websocket error: %s', e)
                time.sleep(reconnect_wait_secs)
                reconnect_wait_secs = min(
                    reconnect_wait_secs * 2, reconnect_wait_secs_max
                )

    async def _ws_processor(self, urls):
        await asyncio.wait([self._get_ws_handler(url) for url in urls])

    def _ws_process(self):
        self._event_loop = get_or_create_event_loop()
        try:
            self._event_loop.run_until_complete(
                self._ws_processor(
                    {f'{self._ws_url}/{sub}/ws' for sub in self._subscriptions}
                )
            )
        except KeyboardInterrupt:
            pass

    def main(self):
        if self._subscriptions:
            self._connect()

    def stop(self):
        if self._ws_proc:
            self._ws_proc.kill()
            self._ws_proc.join()
            self._ws_proc = None

        super().stop()

    @action
    def send_message(
        self,
        topic: str,
        message: str = '',
        server_url: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        title: Optional[str] = None,
        click_url: Optional[str] = None,
        attachment: Optional[str] = None,
        filename: Optional[str] = None,
        actions: Optional[Collection[Mapping[str, str]]] = None,
        email: Optional[str] = None,
        priority: Optional[str] = None,
        tags: Optional[Collection[str]] = None,
        schedule: Optional[str] = None,
    ):
        """
        Send a message/notification to a topic.

        :param topic: Topic where the message will be delivered.
        :param message: Text of the message to be sent.
        :param server_url: Override the default server URL.
        :param username: Set if publishing to the topic requires authentication
        :param password: Set if publishing to the topic requires authentication
        :param title: Custom notification title.
        :param click_url: URL that should be opened when the user clicks the
            notification. It can be an ``http(s)://`` URL, a ``mailto:`, a
            ``geo:``, a link to another ntfy topic (e.g. ``ntfy://mytopic``) or
            a Twitter link (e.g. ``twitter://user?screen_name=myname``).
        :param attachment: Attach a file or URL to the notification. It can
            either be an HTTP URL or a path to a local file.
        :param filename: If ``attachment`` is specified, you can override the
            output filename (default: same filename as the URL/path base name).
        :param actions: List of objects describing possible action buttons
            available for the notification. Supported types:

                - ``view``: Open a URL or an app when the action button is
                  clicked
                - ``http``: Send an HTTP request upon action selection.
                - ``broadcast``: Send an `Android broadcast <https://developer.android.com/guide/components/broadcasts>`
                      intent upon action selection (only available on Android).

            Example:

            .. code-block:: json

                [
                    {
                        "action": "view",
                        "label": "Open portal",
                        "url": "https://home.nest.com/",
                        "clear": true
                    },
                    {
                        "action": "http",
                        "label": "Turn down",
                        "url": "https://api.nest.com/",
                        "method": "PUT",
                        "headers": {
                            "Authorization": "Bearer abcdef..."
                        },
                        "body": "{\\"temperature\\": 65}"
                    },
                    {
                        "action": "broadcast",
                        "label": "Take picture",
                        "intent": "com.myapp.TAKE_PICTURE_INTENT",
                        "extras": {
                            "camera": "front"
                        }
                    }
                ]

        :param email: Forward the notification as an email to the specified
            address.
        :param priority: Custom notification priority. Supported values:
            ``[max, high, default, low, min]``.
        :param tags: Optional list of tags associated with the notification.
            Tag names that match emoji short codes will be rendered as emojis
            in the notification - see `here <https://ntfy.sh/docs/emojis/>` for
            a list of supported emojis.
        :param schedule: Schedule the message to be delivered at a specific
            time (for example, for reminders). Supported formats:

                - UNIX timestamps
                - Duration (e.g. ``30m``, ``3h``, ``2 days``)
                - Natural language strings (e.g. ``Tuesday, 7am`` or
                  ``tomorrow, 3pm``)

        """
        method = requests.post
        url = server_url or self._server_url
        args = {}
        if username and password:
            args['auth'] = (username, password)

        if attachment and not (
            attachment.startswith('http://') or attachment.startswith('https://')
        ):
            url = f'{url}/{topic}'
            attachment = os.path.expanduser(attachment)
            filename = filename or os.path.basename(attachment)
            args['headers'] = {
                'Filename': filename,
                **({'X-Title': title} if title else {}),
                **({'X-Click': click_url} if click_url else {}),
                **({'X-Email': email} if email else {}),
                **({'X-Priority': priority} if priority else {}),
                **({'X-Tags': ','.join(tags)} if tags else {}),
                **({'X-Delay': schedule} if schedule else {}),
            }

            with open(attachment, 'rb') as f:
                args['data'] = f.read()
            method = requests.put
        else:
            args['json'] = {
                'topic': topic,
                'message': message,
                **({'title': title} if title else {}),
                **({'click': click_url} if click_url else {}),
                **({'email': email} if email else {}),
                **({'priority': priority} if priority else {}),
                **({'tags': tags} if tags else {}),
                **({'delay': schedule} if schedule else {}),
                **({'actions': actions} if actions else {}),
                **(
                    {
                        'attach': attachment,
                        'filename': (
                            filename
                            if filename
                            else attachment.split('/')[-1].split('?')[0]
                        ),
                    }
                    if attachment
                    else {}
                ),
            }

        rs = method(url, **args)
        assert rs.ok, 'Could not send message to {}: {}'.format(
            topic, rs.json().get('error', f'HTTP error: {rs.status_code}')
        )

        return rs.json()


# vim:sw=4:ts=4:et:
