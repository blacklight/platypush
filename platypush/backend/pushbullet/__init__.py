import logging
import json
import requests
import websocket

from .. import Backend

class PushbulletBackend(Backend):
    def _init(self, token, device):
        self.token = token
        self.device_name = device
        self.device_id = self.get_device_id()

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

    def get_device_id(self):
        response = requests.get(
            u'https://api.pushbullet.com/v2/devices',
            headers = { 'Access-Token': self.token },
        ).json()

        devices = [dev for dev in response['devices'] if 'nickname' in dev
                   and dev['nickname'] == self.device_name]

        if not devices:
            raise RuntimeError('No such Pushbullet device: {}'
                               .format(self.device_name))

        return devices[0]['iden']

    def send_msg(self, msg):
        if isinstance(msg, dict):
            msg = json.dumps(msg)
        if not isinstance(msg, str):
            raise RuntimeError('Invalid non-JSON message')

        response = requests.post(
            u'https://api.pushbullet.com/v2/pushes',
            headers = { 'Access-Token': self.token },
            json = {
                'type': 'note',
                'device_iden': self.device_id,
                'body': msg,
            }
        ).json()

        if 'dismissed' not in response or response['dismissed'] is True:
            raise RuntimeError('Error while pushing the message: {}'.
                               format(response))

    def run(self):
        self._init_socket()
        logging.info('Initialized Pushbullet backend - device_id: {}'
                     .format(self.device_name))

        self.ws.run_forever()

# vim:sw=4:ts=4:et:

