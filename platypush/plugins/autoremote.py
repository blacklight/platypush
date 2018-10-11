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
            'key': key or self.key,
            'sender': sender or Config.get('device_id'),
        }

        if password or self.password:
            args['password'] = password or self.password

        if target: args['target'] = target
        if ttl: args['ttl'] = ttl
        if group: args['collapseKey'] = group

        response = requests.post(self._AUTOREMOTE_MESSAGE_URL, data=args)
        self.logger.info('Received response from AutoRemote: {}'.format(response.text))

    @action
    def send_notification(self, text=None, key=None, password=None, title=None,
                          target=None, sender=None, ttl=None, group=None,
                          sound=None, vibration=None, url=None, id=None,
                          action=None, icon=None, led=None, ledon=None,
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

        args = {
            'text': text,
            'key': key or self.key,
            'sender': sender or Config.get('device_id'),
        }

        if password or self.password:
            args['password'] = password or self.password

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

