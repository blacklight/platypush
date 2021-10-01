import json
import multiprocessing
from typing import Optional

import requests
import websocket

from platypush.context import get_bus
from platypush.message.event.gotify import GotifyMessageEvent
from platypush.plugins import RunnablePlugin, action
from platypush.schemas.gotify import GotifyMessageSchema


class GotifyPlugin(RunnablePlugin):
    """
    Gotify integration.

    `Gotify <https://gotify.net>`_ allows you process messages and notifications asynchronously
    over your own devices without relying on 3rd-party cloud services.

    Triggers:

        * :class:`platypush.message.event.gotify.GotifyMessageEvent` when a new message is received.

    """

    def __init__(self, server_url: str, app_token: str, client_token: str, **kwargs):
        """
        :param server_url: Base URL of the Gotify server (e.g. ``http://localhost``).
        :param app_token: Application token, required to send message and retrieve application info.
            You can create a new application under ``http://<server_url>/#/applications``.
        :param client_token: Client token, required to subscribe to messages.
            You can create a new client under ``http://<server_url>/#/clients``.
        """
        super().__init__(**kwargs)
        self.server_url = server_url
        self.app_token = app_token
        self.client_token = client_token
        self._ws_app: Optional[websocket.WebSocketApp] = None
        self._state_lock = multiprocessing.RLock()
        self._connected_event = multiprocessing.Event()
        self._disconnected_event = multiprocessing.Event()
        self._ws_listener: Optional[multiprocessing.Process] = None

    def _execute(self, method: str, endpoint: str, **kwargs) -> dict:
        method = method.lower()
        rs = getattr(requests, method)(
            f'{self.server_url}/{endpoint}',
            headers={
                'X-Gotify-Key': self.app_token if method == 'post' else self.client_token,
                'Content-Type': 'application/json',
                **kwargs.pop('headers', {}),
            },
            **kwargs
        )

        rs.raise_for_status()
        try:
            return rs.json()
        except Exception as e:
            self.logger.debug(e)

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

            ws_url = '/'.join([self.server_url.split('/')[0].replace('http', 'ws'), *self.server_url.split('/')[1:]])
            self._ws_app = websocket.WebSocketApp(
                f'{ws_url}/stream?token={self.client_token}',
                on_open=self._on_open(),
                on_message=self._on_msg(),
                on_error=self._on_error(),
                on_close=self._on_close()
            )

            def server():
                self._ws_app.run_forever()

            self._ws_listener = multiprocessing.Process(target=server)
            self._ws_listener.start()

    def _on_open(self):
        def hndl(*_):
            with self._state_lock:
                self._disconnected_event.clear()
                self._connected_event.set()
            self.logger.info('Connected to the Gotify websocket')

        return hndl

    @staticmethod
    def _on_msg():
        def hndl(*args):
            data = json.loads(args[1] if len(args) > 1 else args[0])
            get_bus().post(GotifyMessageEvent(**GotifyMessageSchema().dump(data)))

        return hndl

    def _on_error(self):
        def hndl(*args):
            error = args[1] if len(args) > 1 else args[0]
            ws = args[0] if len(args) > 1 else None
            self.logger.warning('Gotify websocket error: {}'.format(error))
            if ws:
                ws.close()

        return hndl

    def _on_close(self):
        def hndl(*_):
            with self._state_lock:
                self._disconnected_event.set()
                self._connected_event.clear()
            self.logger.warning('Gotify websocket connection closed')

        return hndl

    @action
    def send_message(self, message: str, title: Optional[str] = None, priority: int = 0, extras: Optional[dict] = None):
        """
        Send a message to the server.

        :param message: Message body (Markdown is supported).
        :param title: Message title.
        :param priority: Message priority (default: 0).
        :param extras: Extra JSON payload to be passed on the message.
        :return: .. schema:: gotify.GotifyMessageSchema
        """
        return GotifyMessageSchema().dump(
            self._execute('post', 'message', json={
                'message': message,
                'title': title,
                'priority': priority,
                'extras': extras or {},
            })
        )

    @action
    def get_messages(self, limit: int = 100, since: Optional[int] = None):
        """
        Get a list of the messages received on the server.

        :param limit: Maximum number of messages to retrieve (default: 100).
        :param since: Retrieve the message having ``since`` as minimum ID.
        :return: .. schema:: gotify.GotifyMessageSchema(many=True)
        """
        return GotifyMessageSchema().dump(
            self._execute(
                'get', 'message', params={
                    'limit': limit,
                    **({'since': since} if since else {}),
                }
            ).get('messages', []), many=True
        )

    @action
    def delete_messages(self, *ids):
        """
        Delete messages.

        :param ids: If specified, it deletes the messages matching these IDs.
            Otherwise, it deletes all the received messages.
        """
        if not ids:
            self._execute('delete', 'message')
            return

        for id in ids:
            self._execute('delete', f'message/{id}')


# vim:sw=4:ts=4:et:
