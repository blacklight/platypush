import asyncio
import json
import requests
import time
import websockets

from platypush.config import Config
from platypush.context import get_or_create_event_loop
from platypush.message import Message
from platypush.message.event.pushbullet import PushbulletEvent

from .. import Backend


class PushbulletBackend(Backend):
    """
    This backend will listen for events on a Pushbullet (https://pushbullet.com)
    channel and propagate them to the bus. This backend is quite useful if you
    want to synchronize events and actions with your mobile phone (through the
    Pushbullet app and/or through Tasker), synchronize clipboards, send pictures
    and files to other devices etc. You can also wrap Platypush messages as JSON
    into a push body to execute them.

    Triggers:

        * :class:`platypush.message.event.pushbullet.PushbulletEvent` if a new push is received

    Requires:

        * **requests** (``pip install requests``)
        * **websockets** (``pip install websockets``)
    """

    _PUSHBULLET_WS_URL = 'wss://stream.pushbullet.com/websocket/'
    _WS_PING_INTERVAL = 10

    def __init__(self, token, device='Platypush', **kwargs):
        """
        :param token: Your Pushbullet API token, see https://docs.pushbullet.com/#authentication
        :type token: str

        :param device: Name of the virtual device for Platypush (default: Platypush)
        :type device: str
        """

        super().__init__(**kwargs)

        self.token = token
        self.device_name = device
        self.pb_device_id = self.get_device_id()
        self.ws = None

        self._last_received_msg = {
            'request'  : { 'body': None, 'time': None },
            'response' : { 'body': None, 'time': None },
            'event'    : { 'body': None, 'time': None },
        }

    def _get_latest_push(self):
        t = int(time.time()) - 5
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
            self.logger.exception(e)
            raise e

        if 'pushes' in response and response['pushes']:
            return response['pushes'][0]
        else:
            return {}

    def _should_skip_last_received_msg(self, msg):
        if not isinstance(msg, dict): return True  # We received something weird

        is_duplicate=False
        last_msg = self._last_received_msg[msg['type']]

        if last_msg:
            msg = Message.parse(msg)
            if str(msg) == str(last_msg['body']) \
                    and time.time() - last_msg['time'] <= 2:
                # Duplicate message sent on the Pushbullet socket within
                # two seconds, ignore it
                self.logger.debug('Ignoring duplicate message received on the socket')
                is_duplicate = True

        self._last_received_msg[msg['type']] = {
            'body': msg, 'time': time.time()
        }

        return is_duplicate

    def on_push(self, ws, data):
        try:
            # Parse the push
            try:
                data = json.loads(data) if isinstance(data, str) else data
            except Exception as e:
                self.logger.exception(e)
                return

            # If it's a push, get it
            if data['type'] == 'tickle' and data['subtype'] == 'push':
                push = self._get_latest_push()
            elif data['type'] == 'push':
                push = data['push']
            else: return  # Not a push notification

            # Post an event, useful to react on mobile notifications if
            # you enabled notification mirroring on your PushBullet app
            event = PushbulletEvent(**push)
            self.on_message(event)

            if 'body' not in push: return
            self.logger.debug('Received push: {}'.format(push))

            body = push['body']
            try: body = json.loads(body)
            except ValueError as e: return  # Some other non-JSON push

            if not self._should_skip_last_received_msg(body):
                self.on_message(body)
        except Exception as e:
            self.logger.exception(e)
            return

    def on_error(self, ws, e):
        self.logger.exception(e)

    def _init_socket(self):
        async def pushbullet_client():
            while True:
                try:
                    self.logger.info('Connecting to Pushbullet websocket URL {}'
                                     .format(self._PUSHBULLET_WS_URL))

                    async with websockets.connect(self._PUSHBULLET_WS_URL +
                                                  self.token) as self.ws:
                        self.logger.info('Connection to Pushbullet successful')

                        while True:
                            try:
                                push = await self.ws.recv()
                            except Exception as e:
                                self.logger.exception(e)
                                break

                            self.on_push(self.ws, push)
                except Exception as e:
                    self.logger.exception(e)

        self.close()
        loop = None

        loop = get_or_create_event_loop()
        loop.run_until_complete(pushbullet_client())
        loop.run_forever()


    def create_device(self, name):
        return requests.post(
            u'https://api.pushbullet.com/v2/devices',
            headers = { 'Access-Token': self.token },
            json = {
                'nickname': name,
                'model': 'Platypush virtual device',
                'manufactorer': 'platypush',
                'app_version': 8623,
                'icon': 'system',
            }
        ).json()


    def get_device_id(self):
        response = requests.get(
            u'https://api.pushbullet.com/v2/devices',
            headers = { 'Access-Token': self.token },
        ).json()

        devices = [dev for dev in response['devices'] if 'nickname' in dev
                   and dev['nickname'] == self.device_name]

        if devices:
            return devices[0]['iden']

        try:
            response = self.create_device(self.device_name)
            if 'iden' not in response:
                raise RuntimeError()

            self.logger.info('Created Pushbullet device {}'.format(
                self.device_name))

            return response['iden']
        except Exception as e:
            self.logger.error('Unable to create Pushbillet device {}'.
                                format(self.device_name))

    def send_message(self, msg):
        requests.post(
            u'https://api.pushbullet.com/v2/pushes',
            headers = { 'Access-Token': self.token },
            json = {
                'type': 'note',
                'device_iden': self.pb_device_id,
                'body': str(msg)
            }
        ).json()

    def close(self):
        if self.ws:
            self.ws.close()

    def on_stop(self):
        return self.close()

    def run(self):
        super().run()

        self.logger.info('Initialized Pushbullet backend - device_id: {}'
                     .format(self.device_name))
        self._init_socket()

# vim:sw=4:ts=4:et:

