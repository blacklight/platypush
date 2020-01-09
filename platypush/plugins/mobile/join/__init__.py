import enum
import requests
import threading

from platypush.plugins import Plugin, action


class InterruptionFilterPolicy(enum.Enum):
    ALLOW_ALL = 1
    PRIORITY_ONLY = 2
    BLOCK_ALL = 3
    ALARM_ONLY = 4


class MobileJoinPlugin(Plugin):
    """
    Control mobile devices and other devices linked to Join (https://joaoapps.com/join/api/).
    It requires you to have either the Join app installed on an Android device or the Join
    browser extension installed.

    The ``device`` parameter in the actions can be:

    - A device ID or name
    - A list or comma-separated list of device IDs/names
    - A group name or a list of group names

    Supported groups:

        - group.all
        - group.android
        - group.windows10
        - group.phone
        - group.tablet
        - group.pc

    """

    _base_url = 'https://joinjoaomgcd.appspot.com/_ah/api'
    _push_url = '{}/messaging/v1/sendPush'.format(_base_url)
    _devices_url = '{}/registration/v1/listDevices'.format(_base_url)
    _groups = {
        'group.all',
        'group.android',
        'group.windows10',
        'group.phone',
        'group.tablet',
        'group.pc',
    }

    def __init__(self, api_key: str, **kwargs):
        """
        :param api_key: Join API key. Get your at https://joinjoaomgcd.appspot.com/.
        """
        super().__init__(**kwargs)

        self._api_key = api_key
        self._devices = {}
        self._devices_by_id = {}
        self._devices_by_name = {}
        self._devices_lock = threading.RLock()

    def _send_request(self, url, device=None, params: dict = None, **kwargs):
        if not params:
            params = {}

        params['apikey'] = self._api_key
        if device:
            params['deviceIds'] = self._get_device_ids(device)

        response = requests.get(url, params=params, **kwargs)
        if not response.ok:
            response.raise_for_status()

        response = response.json()
        if response.get('userAuthError'):
            raise PermissionError('Invalid api_key provided')

        del response['userAuthError']
        return response

    def _init_devices(self):
        with self._devices_lock:
            if not self._devices:
                self._devices = self.get_devices().output
                self._devices_by_id = {dev['id']: dev for dev in self._devices}
                self._devices_by_name = {dev['name']: dev for dev in self._devices}

    def _get_device_ids(self, device):
        devices = [dev.strip() for dev in device.split(',')] \
            if isinstance(device, str) else device
        assert isinstance(devices, list)

        has_unknown_devices = True
        cache_refreshed = False
        device_ids = []

        while has_unknown_devices:
            has_unknown_devices = False

            for dev in devices:
                if dev in self._devices_by_id:
                    device_ids.append(self._devices_by_id[dev]['id'])
                elif dev in self._devices_by_name:
                    device_ids.append(self._devices_by_name[dev]['id'])
                elif dev in self._groups:
                    device_ids.append(dev)
                else:
                    has_unknown_devices = True

            if has_unknown_devices:
                if cache_refreshed:
                    raise KeyError('No such device: {}'.format(device))

                self._init_devices()
                cache_refreshed = True

        return device_ids

    @action
    def push(self, device, text=None, url=None, file=None):
        """
        Push a URL or file to one or more devices

        :param device: Device ID or name, or list of device IDs/names, or group name(s)
        :param text: Optional description text for the URL or file
        :param url: URL to be pushed
        :param file: A publicly accessible URL of a file. You can also send the url of a file on your personal
            Google Drive
        """

        assert url or file
        params = {}

        if text:
            params['text'] = text
        if url:
            params['url'] = url
        if file:
            params['file'] = file

        return self._send_request(self._push_url, device=device, params=params)

    @action
    def set_clipboard(self, device, text):
        """
        Write to the clipboard of a device

        :param device: Device ID or name, or list of device IDs/names, or group name(s)
        :param text: Text to be set
        """
        return self._send_request(self._push_url, device=device, params={'clipboard': text})

    @action
    def send_sms(self, device, text: str, number: str = None, contact_name: str = None):
        """
        Send an sms through a mobile device connected to Join

        :param device: Device ID or name, or list of device IDs/names, or group name(s)
        :param text: Text to be sent
        :param number: Phone number
        :param contact_name: Alternatively to the phone number, you can specify a contact name
        """

        assert (number or contact_name) and not (number and contact_name)
        params = {'smstext': text}

        if number:
            params['smsnumber'] = number
        else:
            params['smscontactname'] = contact_name

        return self._send_request(self._push_url, device=device, params=params)

    @action
    def send_mms(self, device, file: str = None, text: str = None, subject: str = '',
                 number: str = None, contact_name: str = None, urgent: bool = False):
        """
        Send an MMS through a mobile device connected to Join

        :param device: Device ID or name, or list of device IDs/names, or group name(s)
        :param text: Text to be sent
        :param number: Phone number
        :param contact_name: Alternatively to the phone number, you can specify a contact name
        :param file: File attached to the message. Must be a local (to the phone) file or a publicly accessible URL
        :param subject: MMS subject
        :param urgent: Set to True if this is an urgent MMS. This will make the sent message be an MMS instead of an SMS
        """

        assert (number or contact_name) and not (number and contact_name)
        params = {
            'mmssubject': subject,
            'mmsurgent': int(urgent),
        }

        if number:
            params['smsnumber'] = number
        else:
            params['smscontactname'] = contact_name
        if file:
            params['mmsfile'] = file
        if text:
            params['smstext'] = text

        return self._send_request(self._push_url, device=device, params=params)

    @action
    def call_number(self, device, number: str):
        """
        Call a phone number through a mobile device connected to Join

        :param device: Device ID or name, or list of device IDs/names, or group name(s)
        :param number: Phone number
        """
        return self._send_request(self._push_url, device=device, params={'callnumber': number})

    @action
    def set_wallpaper(self, device, wallpaper: str):
        """
        Set the wallpaper on a device connected to Join

        :param device: Device ID or name, or list of device IDs/names, or group name(s)
        :param wallpaper: A publicly accessible URL of an image file. Will set the wallpaper on the receiving device
        """
        return self._send_request(self._push_url, device=device, params={'wallpaper': wallpaper})

    @action
    def set_lock_wallpaper(self, device, wallpaper: str):
        """
        Set the lock wallpaper on a device connected to Join

        :param device: Device ID or name, or list of device IDs/names, or group name(s)
        :param wallpaper: A publicly accessible URL of an image file. Will set the lockscreen wallpaper on the receiving
            device if the device has Android 7 or above
        """
        return self._send_request(self._push_url, device=device, params={'wallpaper': wallpaper})

    @action
    def find(self, device):
        """
        Make a device ring loudly
        :param device: Device ID or name, or list of device IDs/names, or group name(s)
        """
        return self._send_request(self._push_url, device=device, params={'find': True})

    @action
    def set_media_volume(self, device, volume: float):
        """
        Set media volume

        :param device: Device ID or name, or list of device IDs/names, or group name(s)
        :param volume: Volume
        """
        return self._send_request(self._push_url, device=device, params={'mediaVolume': volume})

    @action
    def set_ring_volume(self, device, volume: float):
        """
        Set ring volume

        :param device: Device ID or name, or list of device IDs/names, or group name(s)
        :param volume: Volume
        """
        return self._send_request(self._push_url, device=device, params={'ringVolume': volume})

    @action
    def set_alarm_volume(self, device, volume: float):
        """
        Set alarm volume

        :param device: Device ID or name, or list of device IDs/names, or group name(s)
        :param volume: Volume
        """
        return self._send_request(self._push_url, device=device, params={'alarmVolume': volume})

    @action
    def set_interruption_filter(self, device, policy: str):
        """
        Set interruption filter on one or more devices

        :param device: Device ID or name, or list of device IDs/names, or group name(s)
        :param policy: Possible values:

            - 'allow_all': Allow all notifications
            - 'priority_only': Allow only priority notifications and calls
            - 'alarm_only': Allow only alarm-related interruptions
            - 'block_all': Do not allow any interruptions

        """

        try:
            policy = getattr(InterruptionFilterPolicy, policy.upper())
        except AttributeError:
            raise AttributeError('Invalid policy: {}. Supported values: {}'.format(
                policy, [i.name for i in InterruptionFilterPolicy]
            ))

        return self._send_request(self._push_url, device=device, params={'interruptionFilter': policy})

    @action
    def say(self, device, text: str, language: str = None):
        """
        Say some text through a device's TTS engine

        :param device: Device ID or name, or list of device IDs/names, or group name(s)
        :param text: Text to say
        :param language: Language code
        """
        params = {'say': text}
        if language:
            params['language'] = language

        return self._send_request(self._push_url, device=device, params=params)

    @action
    def launch_app(self, device, name: str = None, package: str = None):
        """
        Launch an app on a device

        :param device: Device ID or name, or list of device IDs/names, or group name(s)
        :param name: Application name
        :param package: Alternatively to the application name, you can also specify the application
            package name. You can check the package name for an app by going to its Google Play page and checking
            the end of the URL. Example: for YouTube this is the URL
            (https://play.google.com/store/apps/details?id=com.google.android.youtube) and this is the package name
            (com.google.android.youtube)
        """

        assert (name or package) and not (name and package)

        params = {}
        if name:
            params['app'] = name
        else:
            params['appPackage'] = package

        return self._send_request(self._push_url, device=device, params=params)

    @action
    def send_notification(self, device, title: str = None, text: str = None, url: str = None, file: str = None,
                          icon: str = None, small_icon: str = None, priority: int = 2, vibration_pattern=None,
                          dismiss_on_touch: bool = False, image: str = None, group: str = None,
                          sound: str = None, actions=None):
        """
        Send a notification to a device

        :param device: Device ID or name, or list of device IDs/names, or group name(s)
        :param title: Notification title
        :param text: Notification text
        :param url: URL to be opened on touch
        :param file: A publicly accessible URL of a file that will be opened or downloaded on touch. You can also
            send the url of a file on your personal Google Drive.
        :param icon: If a notification is created on the receiving device and this is set, then it'll be used as
            the notification’s icon. If this image has transparency, it’ll also be used as the status bar icon is
            smallicon is not set. It’ll also be used to tint the notification with its dominating color
        :param small_icon: If a notification is created on the receiving device and this is set, then it’ll be used as
            the notification’s status bar icon
        :param priority: Control how your notification is displayed: lower priority notifications are usually
            displayed lower in the notification list. Values from -2 (lowest priority) to 2 (highest priority).
            Default is 2.
        :param vibration_pattern: If the notification is received on an Android device, the vibration pattern in this
            field will change the way the device vibrates with it. You can easily create a pattern by going to the
            `AutoRemote notification page <http://autoremotejoaomgcd.appspot.com/AutoRemoteNotification.html>`_
            and generate the pattern in the Vibration Pattern field
        :type vibration_pattern: str (comma-separated float values) or list[float]
        :param dismiss_on_touch: If set the notification will be dismissed when touched (default: False)
        :param image: Publicly available URL for an image to show up in the notification
        :param group: Unique ID to group your notifications with
        :param sound: Publicly available URL for a sound to play with the notification
        :param actions: Set notification buttons with customized behaviour. This parameter is a list of Join actions
            configured on the target device that will be mapped to notification input elements.
            More info `on the Joaoapps notifications page <https://joaoapps.com/join/actions/#notifications>`_
        """

        params = {'dismissOnTouch': dismiss_on_touch}

        if title:
            params['title'] = title
        if text:
            params['text'] = text
        if url:
            params['url'] = url
        if file:
            params['file'] = file
        if icon:
            params['icon'] = icon
        if small_icon:
            params['smallIcon'] = small_icon
        if priority:
            params['priority'] = priority
        if vibration_pattern:
            params['vibrationPattern'] = [i for i in vibration_pattern.split(',') if len(i)] \
                if isinstance(vibration_pattern, str) else vibration_pattern
            assert isinstance(params['vibrationPattern'], list)
        if image:
            params['image'] = image
        if group:
            params['group'] = group
        if sound:
            params['sound'] = sound
        if actions:
            actions = [a.strip() for a in actions.split('|||' if '|||' in actions else ',') if len(a.strip())] \
                if isinstance(actions, str) else actions
            assert isinstance(actions, list) and len(actions) > 0
            params['actions'] = '|||'.join(actions)

        return self._send_request(self._push_url, device=device, params=params)

    @action
    def get_devices(self):
        """
        :return: List of connected devices, each containing 'id', 'name', 'user' and 'has_tasker' attributes
        """

        return [
            {
                'id': dev['deviceId'],
                'name': dev['deviceName'],
                'user': dev['userAccount'],
                'has_tasker': dev['hasTasker'],
            }
            for dev in self._send_request(self._devices_url)['records']
        ]


# vim:sw=4:ts=4:et:
