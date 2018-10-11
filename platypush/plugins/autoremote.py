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
    """

    _AUTOREMOTE_BASE_URL = 'https://autoremotejoaomgcd.appspot.com'
    _AUTOREMOTE_MESSAGE_URL = _AUTOREMOTE_BASE_URL + '/sendmessage'
    _AUTOREMOTE_NOTIFICATION_URL = _AUTOREMOTE_BASE_URL + '/sendnotification'

    def __init__(self, key, password=None, *args, **kwargs):
        """
        :param key: The key associated to your device. Open the link in your AutoRemote app and copy the key in the target URL
        :type key: str

        :param password: AutoRemote password configured on the device (default: None)
        :type password: str
        """

        super().__init__(*args, **kwargs)
        self.key = key
        self.password = password

    @action
    def send_message(self, msg, key=None, password=None, target=None,
                     sender=None, ttl=None, group=None, *args, **kwargs):
        """
        Sends a message to AutoRemote.

        :param msg: Message to send

        :param key: Set it if you want to override the default key (default: None)
        :type key: str

        :param password: Set it if you want to override the default password (default: None)
        :type password: str

        :param target: Message target (default: None)
        :type target: str

        :param sender: Message sender (default: None)
        :type target: str

        :param ttl: Message time-to-live in seconds (default: None)
        :type ttl: int

        :param group: Message group name (default: None)
        :type group: str
        """

        args = {
            'message': msg,
            'key': self.key,
            'sender': sender or Config.get('device_id'),
        }

        if self.password: args['password'] = self.password
        if target: args['target'] = target
        if ttl: args['ttl'] = ttl
        if group: args['group'] = group

        response = requests.post(self._AUTOREMOTE_MESSAGE_URL, data=args)
        self.logger.info('Received response from AutoRemote: {}'.format(response.text))


# vim:sw=4:ts=4:et:

