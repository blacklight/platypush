import json
import requests

from platypush.config import Config
from platypush.message import Message
from platypush.plugins import Plugin, action


class AutoremotePlugin(Plugin):
    """
    This plugin allows you to send messages and notifications to an
    Android device that runs AutoRemote (https://joaoapps.com/autoremote/).
    You can also build custom actions to run on your Android device upon
    AutoRemote events using Tasker (https://tasker.joaoapps.com/).

    Requires:

        * **requests** (``pip install requests``)
    """

    _AUTOREMOTE_BASE_URL = 'https://autoremotejoaomgcd.appspot.com'
    _AUTOREMOTE_MESSAGE_URL = _AUTOREMOTE_BASE_URL + '/sendmessage'
    _AUTOREMOTE_NOTIFICATION_URL = _AUTOREMOTE_BASE_URL + '/sendnotification'

    def __init__(self, devices=None, key=None, password=None, *args, **kwargs):
        """
        :param devices: Set this attribute if you want to control multiple AutoRemote devices.
            This will be a map in the format::

                {
                    'device_name': {
                        'key': 'AUTOREMOTE_KEY',
                        'password': 'DEVICE_PASSWORD'
                    },
                    ...
                }

        :type devices: dict

        :param key: The key associated to your device. Open the link in your AutoRemote app
            and copy the key in the target URL. Set this value if you want to communicate
            with only one AutoRemote device.
        :type key: str

        :param password: AutoRemote password configured on the device (default: None).
            Set this value if you want to communicate with only one AutoRemote device.
        :type password: str
        """

        super().__init__(*args, **kwargs)

        if key:
            self.devices = { key: { 'key': key, 'password': password } }
        elif devices:
            self.devices = devices
        else:
            raise RuntimeError('Either <key,password> or devices attributes should be set')

    @action
    def send_message(self, msg, key=None, password=None, devices=None, target=None,
                     sender=None, ttl=None, group=None, *args, **kwargs):
        """
        Sends a message to AutoRemote.

        :param msg: Message to send

        :param key: Set it if you want to override the default devices
            (default: None, message sent to all the configured devices)
        :type key: str

        :param password: Set it if you want to override the default password (default: None)
        :type password: str

        :param devices: Set it if you want to send the message to a specific list of
            configured devices (default: None, message sent to all the configured devices)
        :type devices: list

        :param target: Message target (default: None)
        :type target: str

        :param sender: Message sender (default: None)
        :type target: str

        :param ttl: Message time-to-live in seconds (default: None)
        :type ttl: int

        :param group: Message group name (default: None)
        :type group: str
        """

        target_devices = []

        if devices:
            target_devices = [self.devices[name] for name in self.devices.keys()
                              if name in devices]
        elif key:
            device = { 'key': key }
            if password:
                device['password'] = password

            target_devices = [device]
        else:
            target_devices = self.devices.values()

        for device in target_devices:
            args = {
                'message': msg,
                'key': device['key'],
                'sender': sender or Config.get('device_id'),
            }

            if device.get('password'):
                args['password'] = device['password']

            if target: args['target'] = target
            if ttl: args['ttl'] = ttl
            if group: args['collapseKey'] = group

            response = requests.post(self._AUTOREMOTE_MESSAGE_URL, data=args)
            self.logger.info('Received response from AutoRemote: {}'.format(response.text))

    @action
    def send_notification(self, text=None, key=None, password=None, devices=None,
                          title=None, target=None, sender=None, ttl=None,
                          group=None, sound=None, vibration=None, url=None,
                          id=None, action=None, icon=None, led=None, ledon=None,
                          ledoff=None, picture=None, share=False, msg=None,
                          action1=None, action1_name=None, action1_icon=None,
                          action2=None, action2_name=None, action2_icon=None,
                          action3=None, action3_name=None, action3_icon=None,
                          persistent=False, statusbar_icon=None, ticker=None,
                          dismiss_on_touch=False, priority=0, number=None,
                          content_info=None, subtext=None, max_progress=None,
                          progress=None, indeterminate_progress=False,
                          action_on_dismiss=None, cancel=False, *args, **kwargs):
        """
        Sends a notification to AutoRemote. Click on your AutoRemote URL ->
        Send Notification for a detailed explanation of the attributes.
        """

        target_devices = []

        if devices:
            target_devices = [self.devices[name] for name in self.devices.keys()
                              if name in devices]
        elif key:
            device = { 'key': key }
            if password:
                device['password'] = password

            target_devices = [device]
        else:
            target_devices = self.devices.values()

        for device in target_devices:
            args = {
                'text': text,
                'key': device.get('key'),
                'sender': sender or Config.get('device_id'),
            }

            if device.get('password'):
                args['password'] = device['password']

            if target: args['target'] = target
            if ttl: args['ttl'] = ttl
            if group: args['collapseKey'] = group
            if title: args['title'] = title
            if text: args['text'] = text
            if sound: args['sound'] = sound
            if vibration: args['vibration'] = vibration
            if url: args['url'] = url
            if id: args['id'] = id
            if action: args['action'] = action
            if icon: args['icon'] = icon
            if led: args['led'] = led
            if ledon: args['ledon'] = ledon
            if ledoff: args['ledoff'] = ledoff
            if picture: args['picture'] = picture
            if msg: args['message'] = msg
            if share: args['share'] = share
            if action1: args['action1'] = action1
            if action1_name: args['action1name'] = action1_name
            if action1_icon: args['action1icon'] = action1_icon
            if action2: args['action2'] = action2
            if action2_name: args['action2name'] = action2_name
            if action2_icon: args['action2icon'] = action2_icon
            if action3: args['action3'] = action3
            if action3_name: args['action3name'] = action3_name
            if action3_icon: args['action3icon'] = action3_icon
            if persistent: args['persistent'] = persistent
            if statusbar_icon: args['statusbaricon'] = statusbar_icon
            if ticker: args['ticker'] = ticker
            if dismiss_on_touch: args['dismissontouch'] = dismiss_on_touch
            if priority: args['priority'] = priority
            if number: args['number'] = number
            if content_info: args['contentinfo'] = content_info
            if subtext: args['subtext'] = subtext
            if max_progress: args['maxprogress'] = max_progress
            if progress: args['progress'] = progress
            if indeterminate_progress: args['indeterminateprogress'] = indeterminate_progress
            if action_on_dismiss: args['actionondismiss'] = action_on_dismiss
            if cancel: args['cancel'] = cancel

            response = requests.post(self._AUTOREMOTE_NOTIFICATION_URL, data=args)
            self.logger.info('Received response from AutoRemote: {}'.format(response.text))


# vim:sw=4:ts=4:et:

