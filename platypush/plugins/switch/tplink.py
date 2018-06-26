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

    def _scan(self):
        return Discover.discover()

    def status(self):
        """
        :returns: The available device over the network as a
        """

        devices = dict(
            (ip, {
                'alias': dev.alias,
                'current_consumption': dev.current_consumption,
                'host': dev.host,
                'hw_info': dev.hw_info,
                'on': dev.is_on,
            })

            for (ip, dev) in self._scan()
        )

        return Response(output=devices)

    def on(self, device):
        """
        Turn on a device

        :param device: Device IP or hostname
        :type device: str
        """

        devices = self._scan()
        if device not in devices:
            raise RuntimeError('Device {} not found'.format(device))

        devices[device].turn_on()
        return Response(output={'status':'on'})


    def off(self, device):
        """
        Turn off a device

        :param device: Device IP or hostname
        :type device: str
        """

        devices = self._scan()
        if device not in devices:
            raise RuntimeError('Device {} not found'.format(device))

        devices[device].turn_off()
        return Response(output={'status':'off'})


    def toggle(self, device):
        """
        Toggle the state of a device (on/off)

        :param device: Device IP or hostname
        :type device: str
        """

        devices = self._scan()
        if device not in devices:
            raise RuntimeError('Device {} not found'.format(device))

        dev = devices[device]
        is_on = dev.is_on

        if is_on:
            dev.turn_off()
        else:
            dev.turn_on()

        return Response(output={'status': 'off' if is_on else 'on'})


# vim:sw=4:ts=4:et:

