import json

from ouimeaux.environment import Environment, UnknownDevice
from platypush.plugins import action
from platypush.plugins.switch import SwitchPlugin


class SwitchWemoPlugin(SwitchPlugin):
    """
    Plugin to control a Belkin WeMo smart switch
    (https://www.belkin.com/us/Products/home-automation/c/wemo-home-automation/)

    Requires:

        * **ouimeaux** (``pip install ouimeaux``)
    """

    def __init__(self, discovery_seconds=3, *args, **kwargs):
        """
        :param discovery_seconds: Discovery time when scanning for devices (default: 3)
        :type discovery_seconds: int
        """

        super().__init__(*args, **kwargs)
        self.discovery_seconds=discovery_seconds
        self.env = Environment()
        self.env.start()
        self.refresh_devices()

    def refresh_devices(self):
        """ Update the list of available devices """
        self.logger.info('Starting WeMo discovery')
        self.env.discover(seconds=self.discovery_seconds)
        self.devices = self.env.devices

    @action
    def get_devices(self):
        """
        Get the list of available devices
        :returns: The list of devices.

        Example output::

            output = {
                "devices": [
                    {
                        "host": "192.168.1.123",
                        "name": "Switch 1",
                        "state": 1,
                        "model": "Belkin Plugin Socket 1.0",
                        "serialnumber": "123456ABCDEF"
                    },

                    {
                        # ...
                    }
                ]
            }
        """
        self.refresh_devices()
        return {
            'devices': [
                {
                    'host': dev.host,
                    'name': dev.name,
                    'state': dev.get_state(),
                    'model': dev.model,
                    'serialnumber': dev.serialnumber,
                }
                for (name, dev) in self.devices.items()
            ]
        }

    def _exec(self, method, device, *args, **kwargs):
        if device not in self.devices:
            self.refresh_devices()

        if device not in self.devices:
            raise RuntimeError('Device {} not found'.format(device))

        self.logger.info('{} -> {}'.format(device, method))
        dev = self.devices[device]
        getattr(dev, method)(*args, **kwargs)

        return {'device': device, 'state': dev.get_state()}

    @action
    def on(self, device):
        """
        Turn a switch on

        :param device: Device name
        :type device: str
        """
        return self._exec('on', device)

    @action
    def off(self, device):
        """
        Turn a switch off

        :param device: Device name
        :type device: str
        """
        return self._exec('off', device)

    @action
    def toggle(self, device):
        """
        Toggle the state of a switch (on/off)

        :param device: Device name
        :type device: str
        """
        return self._exec('toggle', device)


# vim:sw=4:ts=4:et:

