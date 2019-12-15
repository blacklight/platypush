import ipaddress

from platypush.plugins import action
from platypush.plugins.switch import SwitchPlugin
from platypush.utils.workers import Workers
from .lib import WemoRunner
from .scanner import Scanner


class SwitchWemoPlugin(SwitchPlugin):
    """
    Plugin to control a Belkin WeMo smart switches
    (https://www.belkin.com/us/Products/home-automation/c/wemo-home-automation/)

    Requires:

        * **requests** (``pip install requests``)
    """

    _default_port = 49153

    def __init__(self, devices=None, netmask: str = None, port: int = _default_port, **kwargs):
        """
        :param devices: List of IP addresses or name->address map containing the WeMo Switch devices to control.
            This plugin previously used ouimeaux for auto-discovery but it's been dropped because
            1. too slow 2. too heavy 3. auto-discovery failed too often.
        :type devices: list or dict

        :param netmask: Alternatively to a list of static IP->name pairs,  you can specify the network mask where
            the devices should be scanned (e.g. '192.168.1.0/24')

        :param port: Port where the WeMo devices are expected to expose the RPC/XML over HTTP service (default: 49153)
        """

        super().__init__(**kwargs)
        self.port = port
        self.netmask = netmask
        self._devices = {}
        self._init_devices(devices)

    def _init_devices(self, devices):
        if devices:
            self._devices.update(devices if isinstance(devices, dict) else
                                 {addr: addr for addr in devices})
        else:
            self._devices = {}

        self._addresses = set(self._devices.values())

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
                        "on": true,
                    },

                    {
                        # ...
                    }
                ]
        """

        return [
                self.status(device).output
                for device in self._devices.values()
        ]

    def _get_address(self, device: str) -> str:
        if device not in self._addresses:
            try:
                return self._devices[device]
            except KeyError:
                pass

        return device

    @action
    def status(self, device: str = None, *args, **kwargs):
        devices = {device: device} if device else self._devices.copy()

        ret = [
            {
                'id': addr,
                'ip': addr,
                'name': name if name != addr else WemoRunner.get_name(addr),
                'on': WemoRunner.get_state(addr),
            }
            for (name, addr) in devices.items()
        ]

        return ret[0] if device else ret

    @action
    def on(self, device: str, **kwargs):
        """
        Turn a switch on

        :param device: Device name or address
        """
        device = self._get_address(device)
        WemoRunner.on(device)
        return self.status(device)

    @action
    def off(self, device: str, **kwargs):
        """
        Turn a switch off

        :param device: Device name or address
        """
        device = self._get_address(device)
        WemoRunner.off(device)
        return self.status(device)

    @action
    def toggle(self, device: str, *args, **kwargs):
        """
        Toggle a device on/off state

        :param device: Device name or address
        """
        device = self._get_address(device)
        WemoRunner.toggle(device)
        return self.status(device)

    @action
    def get_state(self, device: str):
        """
        Get the on state of a device (True/False)

        :param device: Device name or address
        """
        device = self._get_address(device)
        return WemoRunner.get_state(device)

    @action
    def get_name(self, device: str):
        """
        Get the friendly name of a device

        :param device: Device name or address
        """
        device = self._get_address(device)
        return WemoRunner.get_name(device)

    @action
    def scan(self, netmask: str = None):
        netmask = netmask or self.netmask
        assert netmask, 'Scan not supported: No netmask specified'

        workers = Workers(10, Scanner, port=self.port)
        with workers:
            for addr in ipaddress.IPv4Network(netmask):
                workers.put(addr.exploded)

        devices = {
            dev.name: dev.addr
            for dev in workers.responses
        }

        self._init_devices(devices)
        return self.status()


# vim:sw=4:ts=4:et:
