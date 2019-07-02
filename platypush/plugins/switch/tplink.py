from pyHS100 import Discover

from platypush.plugins import action
from platypush.plugins.switch import SwitchPlugin


class SwitchTplinkPlugin(SwitchPlugin):
    """
    Plugin to interact with TP-Link smart switches/plugs like the HS100
    (https://www.tp-link.com/us/products/details/cat-5516_HS100.html).

    Requires:

        * **pyHS100** (``pip install pyHS100``)
    """

    _ip_to_dev = {}
    _alias_to_dev = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _scan(self):
        devices = Discover.discover()
        self._ip_to_dev = {}
        self._alias_to_dev = {}

        for (ip, dev) in devices.items():
            self._ip_to_dev[ip] = dev
            self._alias_to_dev[dev.alias] = dev

        return devices

    def _get_device(self, device, use_cache=True):
        if not use_cache:
            self._scan()

        if device in self._ip_to_dev:
            return self._ip_to_dev[device]

        if device in self._alias_to_dev:
            return self._alias_to_dev[device]

        if use_cache:
            return self._get_device(device, use_cache=False)
        else:
            raise RuntimeError('Device {} not found'.format(device))

    @action
    def on(self, device, **kwargs):
        """
        Turn on a device

        :param device: Device IP, hostname or alias
        :type device: str
        """

        device = self._get_device(device)
        device.turn_on()
        return self.status(device)

    @action
    def off(self, device, **kwargs):
        """
        Turn off a device

        :param device: Device IP, hostname or alias
        :type device: str
        """

        device = self._get_device(device)
        device.turn_off()
        return self.status(device)

    @action
    def toggle(self, device, **kwargs):
        """
        Toggle the state of a device (on/off)

        :param device: Device IP, hostname or alias
        :type device: str
        """

        device = self._get_device(device)

        if device.is_on:
            device.turn_off()
        else:
            device.turn_on()

        return {
            'current_consumption': device.current_consumption(),
            'id': device.host,
            'ip': device.host,
            'host': device.host,
            'hw_info': device.hw_info,
            'name': device.alias,
            'on': device.is_on,
        }

    @property
    def devices(self):
        return [
            {
                'current_consumption': dev.current_consumption(),
                'id': ip,
                'ip': ip,
                'host': dev.host,
                'hw_info': dev.hw_info,
                'name': dev.alias,
                'on': dev.is_on,
            } for (ip, dev) in self._scan().items()
        ]


# vim:sw=4:ts=4:et:
