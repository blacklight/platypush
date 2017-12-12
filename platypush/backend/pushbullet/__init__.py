import logging
import json
import websocket

from pushbullet import Pushbullet

from .. import Backend

class PushbulletBackend(Backend):
    _requires = [
        'pushbullet'
    ]

    def _init(self, token, device):
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
        self.ws.close()
        self._init_socket()

    def _on_push(self, data):
        try:
            data = json.loads(data) if isinstance(data, str) else push
        except Exception as e:
            logging.exception(e)
            return

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

    def _init_socket(self):
        self.ws = websocket.WebSocketApp(
            'wss://stream.pushbullet.com/websocket/' + self.token,
            on_open = self._on_init,
            on_message = self._on_msg,
            on_error = self._on_error,
            on_close = self._on_close)

        self.ws.backend = self

    def send_msg(self, msg):
        if isinstance(msg, dict):
            msg = json.dumps(msg)
        if not isinstance(msg, str):
            raise RuntimeError('Invalid non-JSON message')

        pb = Pushbullet(self.token)
        devices = [dev for dev in pb.devices if dev.nickname == self.device]
        if not devices:
            raise RuntimeError('No such device: {}'.format(self.device))

        device = devices[0]
        pb.push_note('', msg, device)

    def run(self):
        self._init_socket()
        logging.info('Initialized Pushbullet backend - device_id: {}'
                     .format(self.device))

        self.ws.run_forever()

# vim:sw=4:ts=4:et:

