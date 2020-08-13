import json
import time
from typing import Optional

from platypush.backend import Backend
from platypush.message.event.pushbullet import PushbulletEvent


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
        * **pushbullet.py** (``pip install git+https://github.com/rbrcsk/pushbullet.py``)
    """

    def __init__(self, token: str, device: str = 'Platypush', proxy_host: Optional[str] = None,
                 proxy_port: Optional[int] = None, **kwargs):
        """
        :param token: Your Pushbullet API token, see https://docs.pushbullet.com/#authentication
        :param device: Name of the virtual device for Platypush (default: Platypush)
        :param proxy_host: HTTP proxy host (default: None)
        :param proxy_port: HTTP proxy port (default: None)
        """
        super().__init__(**kwargs)

        self.token = token
        self.device_name = device
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.device = None
        self.pb_device_id = None
        self.pb = None
        self.listener = None

    def _initialize(self):
        # noinspection PyPackageRequirements
        from pushbullet import Pushbullet
        self.pb = Pushbullet(self.token)

        # noinspection PyBroadException
        try:
            self.device = self.pb.get_device(self.device_name)
        except:
            self.device = self.pb.new_device(self.device_name)

        self.pb_device_id = self.get_device_id()

    def _get_latest_push(self):
        t = int(time.time()) - 5
        pushes = self.pb.get_pushes(modified_after=str(t), limit=1)
        if pushes:
            return pushes[0]

    def on_push(self):
        def callback(data):
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
                else:
                    return  # Not a push notification

                if not push:
                    return

                # Post an event, useful to react on mobile notifications if
                # you enabled notification mirroring on your PushBullet app
                event = PushbulletEvent(**push)
                self.on_message(event)

                if 'body' not in push:
                    return
                self.logger.debug('Received push: {}'.format(push))

                body = push['body']
                try:
                    body = json.loads(body)
                    self.on_message(body)
                except Exception as e:
                    self.logger.debug(('Unexpected message received on the ' +
                                       'Pushbullet backend: {}. Message: {}')
                                      .format(str(e), body))

            except Exception as e:
                self.logger.exception(e)
                return

        return callback

    def get_device_id(self):
        # noinspection PyBroadException
        try:
            return self.pb.get_device(self.device_name).device_iden
        except Exception:
            device = self.pb.new_device(self.device_name, model='Platypush virtual device',
                                        manufacturer='platypush', icon='system')

            self.logger.info('Created Pushbullet device {}'.format(
                self.device_name))

            return device.device_iden

    def close(self):
        if self.listener:
            self.listener.close()

    def on_stop(self):
        super().on_stop()
        return self.close()

    def run(self):
        # noinspection PyPackageRequirements
        from pushbullet import Listener
        super().run()
        initialized = False

        while not initialized:
            try:
                self._initialize()
                initialized = True
            except Exception as e:
                self.logger.exception(e)
                self.logger.error('Pushbullet initialization error: {}'.format(str(e)))
                time.sleep(30)

        self.logger.info('Initialized Pushbullet backend - device_id: {}'
                         .format(self.device_name))

        self.listener = Listener(account=self.pb, on_push=self.on_push(),
                                 http_proxy_host=self.proxy_host,
                                 http_proxy_port=self.proxy_port)

        self.listener.run_forever()

# vim:sw=4:ts=4:et:
