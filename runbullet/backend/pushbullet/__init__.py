import logging
import json
import websocket

from .. import Backend

class PushbulletBackend(Backend):
    def _init(self, token, device=None):
        self.token = token
        self.device = device

    @staticmethod
    def _on_init(ws):
        logging.info('Connection opened')

    @staticmethod
    def _on_close(ws):
        logging.info('Connection closed')

    @staticmethod
    def _on_msg(ws, msg):
        ws.backend._on_push(msg)

    @staticmethod
    def _on_error(ws, e):
        logging.exception(e)

    def _on_push(self, data):
        data = json.loads(data) if isinstance(data, str) else push

        if data['type'] != 'push':
            return  # Not a push notification

        push = data['push']
        logging.debug('Received push: {}'.format(push))

        if 'body' not in push:
            return

        body = push['body']
        try:
            body = json.loads(body)
        except ValueError as e:
            return

        self.on_msg(body)

    def run(self):
        self.ws = websocket.WebSocketApp(
            'wss://stream.pushbullet.com/websocket/' + self.token,
            on_open = self._on_init,
            on_message = self._on_msg,
            on_error = self._on_error,
            on_close = self._on_close)

        self.ws.backend = self
        self.ws.run_forever()

# vim:sw=4:ts=4:et:

