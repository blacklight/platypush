from platypush.plugins import action
from platypush.plugins.switch import SwitchPlugin


class SwitchWemoPlugin(SwitchPlugin):
    """
    Plugin to control a Belkin WeMo smart switches
    (https://www.belkin.com/us/Products/home-automation/c/wemo-home-automation/)

    Requires:

        * **ouimeaux** (``pip install ouimeaux``)
    """

    def __init__(self, discovery_seconds=3, **kwargs):
        """
        :param discovery_seconds: Discovery time when scanning for devices (default: 3)
        :type discovery_seconds: int
        """

        super().__init__(**kwargs)
        self.discovery_seconds = discovery_seconds
        self.env = None

    def _refresh_devices(self):
        """ Update the list of available devices """
        self.logger.info('Starting WeMo discovery')
        self._get_environment()
        self.env.discover(seconds=self.discovery_seconds)
        self._devices = self.env.devices

    def _get_environment(self):
        if not self.env:
            from ouimeaux.environment import Environment
            self.env = Environment()
            self.env.start()
            self._refresh_devices()

    @property
    def devices(self):
        """
        Get the list of available devices
        :returns: The list of devices.

        Example output::

            output = [
                    {
                        "ip": "192.168.1.123",
                        "name": "Switch 1",
                        "state": 1,
                        "model": "Belkin Plugin Socket 1.0",
                        "serialnumber": "123456ABCDEF"
                    },

                    {
                        # ...
                    }
                ]
        """
        self._refresh_devices()

        return [
            {
                'id': dev.name,
                'ip': dev.host,
                'name': dev.name,
                'model': dev.model,
                'on': True if dev.get_state() else False,
                'serialnumber': dev.serialnumber,
            }
            for (name, dev) in self._devices.items()
        ]

    def _exec(self, method, device, *args, **kwargs):
        self._get_environment()

        if device not in self._devices:
            self._refresh_devices()

        if device not in self._devices:
            raise RuntimeError('Device {} not found'.format(device))

        self.logger.info('Executing {} on WeMo device {}'.
                         format(method, device))
        dev = self._devices[device]
        getattr(dev, method)(*args, **kwargs)

        return self.status(device)

    @action
    def on(self, device, **kwargs):
        """
        Turn a switch on

        :param device: Device name
        :type device: str
        """
        return self._exec('on', device)

    @action
    def off(self, device, **kwargs):
        """
        Turn a switch off

        :param device: Device name
        :type device: str
        """
        return self._exec('off', device)

    @action
    def toggle(self, device, **kwargs):
        """
        Toggle the state of a switch (on/off)

        :param device: Device name
        :type device: str
        """
        return self._exec('toggle', device)


# vim:sw=4:ts=4:et:
