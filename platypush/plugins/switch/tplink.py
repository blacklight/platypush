from pyHS100 import Discover

from platypush.message.response import Response
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


    def status(self):
        """
        :returns: The available device over the network as a
        """

        devices = { 'devices': {
            ip: {
                'alias': dev.alias,
                'current_consumption': dev.current_consumption(),
                'host': dev.host,
                'hw_info': dev.hw_info,
                'on': dev.is_on,
            } for (ip, dev) in self._scan().items()
        } }

        return Response(output=devices)

    def on(self, device):
        """
        Turn on a device

        :param device: Device IP, hostname or alias
        :type device: str
        """

        device = self._get_device(device)
        device.turn_on()
        return Response(output={'status':'on'})


    def off(self, device):
        """
        Turn off a device

        :param device: Device IP, hostname or alias
        :type device: str
        """

        device = self._get_device(device)
        device.turn_off()
        return Response(output={'status':'off'})


    def toggle(self, device):
        """
        Toggle the state of a device (on/off)

        :param device: Device IP, hostname or alias
        :type device: str
        """

        device = self._get_device(device, use_cache=False)

        if device.is_on:
            device.turn_off()
        else:
            device.turn_on()

        return Response(output={'status': 'off' if device.is_off else 'on'})


# vim:sw=4:ts=4:et:

