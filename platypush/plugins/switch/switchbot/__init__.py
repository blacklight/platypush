import struct
import subprocess
import time

from bluetooth.ble import DiscoveryService, GATTRequester

from platypush.plugins import action
from platypush.plugins.switch import SwitchPlugin


class Scanner(object):
    """
    XXX The Scanner object doesn't work. Add your devices by address statically to the plugin configuration for now
    instead of relying on scanning capabilities
    """

    service_uuid = '1bc5d5a5-0200b89f-e6114d22-000da2cb'

    def __init__(self, bt_interface=None, timeout_secs=None):
        self.bt_interface = bt_interface
        self.timeout_secs = timeout_secs if timeout_secs else 2

    @classmethod
    def _get_uuids(cls, device):
        uuids = set()

        for uuid in device['uuids']:
            if isinstance(uuid, tuple):
                uuid = ''
                for i in range(0, len(uuid)):
                    token = struct.pack('<I', uuid[i])
                    for byte in token:
                        uuid += hex(byte)[2:].zfill(2)
                    uuid += ('-' if i < len(uuid)-1 else '')
                uuids.add(uuid)
            else:
                uuids.add(hex(uuid)[2:])

        return uuids

    def scan(self):
        service = DiscoveryService(self.bt_interface) \
            if self.bt_interface else DiscoveryService()

        devices = service.discover(self.timeout_secs)
        return sorted([addr for addr, device in devices.items()
                       if self.service_uuid in self._get_uuids(device)])


class Driver(object):
    handle = 0x16
    commands = {
        'press': '\x57\x01\x00',
        'on': '\x57\x01\x01',
        'off': '\x57\x01\x02',
    }

    def __init__(self, device, bt_interface=None, timeout_secs=None):
        self.device = device
        self.bt_interface = bt_interface
        self.timeout_secs = timeout_secs if timeout_secs else 5
        self.req = None

    def connect(self):
        if self.bt_interface:
            self.req = GATTRequester(self.device, False, self.bt_interface)
        else:
            self.req = GATTRequester(self.device, False)

        self.req.connect(True, 'random')
        connect_start_time = time.time()

        while not self.req.is_connected():
            if time.time() - connect_start_time >= self.timeout_secs:
                raise RuntimeError('Connection to {} timed out after {} seconds'
                                   .format(self.device, self.timeout_secs))

    def run_command(self, command):
        self.req.write_by_handle(self.handle, self.commands[command])
        data = self.req.read_by_handle(self.handle)
        return data


class SwitchSwitchbotPlugin(SwitchPlugin):
    """
    Plugin to interact with a Switchbot (https://www.switch-bot.com/) device and
    programmatically control buttons.

    NOTE: since the interaction with the Switchbot requires root privileges
    (in order to scan on the bluetooth interface or setting gattlib in random),
    this plugin just wraps the module into a `sudo` flavor, since running
    Platypush with root privileges should be considered as a very bad idea.
    Make sure that your user has sudo privileges for running this plugin.

    Requires:

        * **pybluez** (``pip install pybluez``)
        * **gattlib** (``pip install gattlib``)
        * **libboost** (on Debian ```apt-get install libboost-python-dev libboost-thread-dev``)
    """

    def __init__(self, bt_interface=None, connect_timeout=None,
                 scan_timeout=None, devices=None, **kwargs):
        """
        :param bt_interface: Bluetooth interface to use (e.g. hci0) default: first available one
        :type bt_interface: str

        :param connecct_timeout: Timeout for the conncection to the Switchbot device - default: None
        :type connect_timeout: float

        :param scan_timeout: Timeout for the scan operations - default: None
        :type scan_timeout: float

        :param devices: Devices to control, as a BMAC address -> name map
        :type devices: dict
        """

        super().__init__(**kwargs)

        if devices is None:
            devices = {}

        self.bt_interface = bt_interface
        self.connect_timeout = connect_timeout if connect_timeout else 5
        self.scan_timeout = scan_timeout if scan_timeout else 2
        self.configured_devices = devices
        self.configured_devices_by_name = {
            name: addr
            for addr, name in self.configured_devices.items()
        }

    def _run(self, device, command=None):
        if device in self.configured_devices_by_name:
            device = self.configured_devices_by_name[device]

        try:
            # XXX this requires sudo and it's executed in its own process
            # because the Switchbot plugin requires root privileges to send
            # raw bluetooth messages on the interface. Make sure that the user
            # that runs platypush has the right permissions to run this with sudo
            output = subprocess.check_output((
                'sudo python3 -m platypush.plugins.switch.switchbot ' +
                '--device {} ' +
                ('--interface {} '.format(self.bt_interface) if self.bt_interface else '') +
                ('--connect-timeout {} '.format(self.connect_timeout) if self.connect_timeout else '') +
                ('--{} '.format(command) if command else '')).format(device),
                stderr=subprocess.STDOUT, shell=True).decode('utf-8')
        except subprocess.CalledProcessError as e:
            raise RuntimeError(e.output.decode('utf-8'))

        self.logger.info('Output of switchbot command: {}'.format(output))
        return self.status(device)

    @action
    def press(self, device):
        """
        Send a press button command to a device

        :param device: Device name or address
        :type device: str
        """
        return self._run(device)

    @action
    def toggle(self, device, **kwargs):
        return self.press(device)

    @action
    def on(self, device, **kwargs):
        """
        Send a press-on button command to a device

        :param device: Device name or address
        :type device: str
        """
        return self._run(device, 'on')

    @action
    def off(self, device, **kwargs):
        """
        Send a press-off button command to a device

        :param device: Device name or address
        :type device: str
        """
        return self._run(device, 'off')

    @action
    def scan(self):
        """
        Scan for available Switchbot devices nearby.
        XXX This action doesn't work for now. Configure your devices statically for now instead of
        relying on the scanner
        """
        try:
            return subprocess.check_output(
                'sudo python3 -m platypush.plugins.switch.switchbot --scan ' +
                ('--interface {} '.format(self.bt_interface) if self.bt_interface else '') +
                ('--scan-timeout {} '.format(self.scan_timeout) if self.scan_timeout else ''),
                stderr=subprocess.STDOUT, shell=True).decode('utf-8')
        except subprocess.CalledProcessError as e:
            raise RuntimeError(e.output.decode('utf-8'))

    @property
    def devices(self):
        return [
            {
                'address': addr,
                'id': addr,
                'name': name,
                'on': False,
            }
            for addr, name in self.configured_devices.items()
        ]


# vim:sw=4:ts=4:et:
