import logging
import json
import requests
import time
import websocket

from platypush.config import Config
from platypush.message import Message

from .. import Backend

class PushbulletBackend(Backend):
    def __init__(self, token, device, **kwargs):
        super().__init__(**kwargs)

        self.token = token
        self.device_name = device
        self.pb_device_id = self.get_device_id()

        self._last_received_msg = {
            'request': { 'body': None, 'time': None },
            'response': { 'body': None, 'time': None },
        }

    def _get_latest_push(self):
        t = int(time.time()) - 2
        try:
            response = requests.get(
                u'https://api.pushbullet.com/v2/pushes',
                headers = { 'Access-Token': self.token },
                params  = {
                    'modified_after': str(t),
                    'active' : 'true',
                    'limit'  : 1,
                }
            )

            response = response.json()
        except Exception as e:
            logging.exception(e)
            raise e

        if 'pushes' in response and response['pushes']:
            return response['pushes'][0]
        else:
            return {}

    def _should_skip_last_received_msg(self, msg):
        is_duplicate=False
        last_msg = self._last_received_msg[msg['type']]

        if last_msg:
            msg = Message.parse(msg)
            if str(msg) == str(last_msg['body']) \
                    and time.time() - last_msg['time'] <= 2:
                # Duplicate message sent on the Pushbullet socket within
                # two seconds, ignore it
                logging.debug('Ignoring duplicate message received on the socket')
                is_duplicate = True

        self._last_received_msg[msg['type']] = {
            'body': msg, 'time': time.time()
        }

        return is_duplicate

    @staticmethod
    def _on_msg(backend):
        def _f(ws, data):
            try:
                data = json.loads(data) if isinstance(data, str) else push
            except Exception as e:
                logging.exception(e)
                return

            if data['type'] == 'tickle' and data['subtype'] == 'push':
                push = backend._get_latest_push()
            elif data['type'] == 'push':
                push = data['push']
            else:
                return  # Not a push notification

            logging.debug('Received push: {}'.format(push))

            if 'body' not in push: return

            body = push['body']
            try: body = json.loads(body)
            except ValueError as e: return

            if not backend._should_skip_last_received_msg(body):
                backend.on_msg(body)

        return _f

    @staticmethod
    def _on_error(backend):
        def _f(ws, e):
            logging.exception(e)
            logging.info('Restarting PushBullet backend')
            ws.close()
            backend._init_socket()

        return _f

    def _init_socket(self):
        self.ws = websocket.WebSocketApp(
            'wss://stream.pushbullet.com/websocket/' + self.token,
            # on_message = self._on_msg,
            on_message = self._on_msg(self),
            on_error = self._on_error(self))

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

    def _send_msg(self, msg):
        requests.post(
            u'https://api.pushbullet.com/v2/pushes',
            headers = { 'Access-Token': self.token },
            json = {
                'type': 'note',
                'device_iden': self.pb_device_id,
                'body': str(msg)
            }
        ).json()

    def run(self):
        self._init_socket()
        logging.info('Initialized Pushbullet backend - device_id: {}'
                     .format(self.device_name))

        self.ws.run_forever()

# vim:sw=4:ts=4:et:

