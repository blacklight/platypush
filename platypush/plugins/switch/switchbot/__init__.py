import struct
import subprocess
import time

from bluetooth.ble import DiscoveryService, GATTRequester

from platypush.message.response import Response

from .. import SwitchPlugin

class Scanner(object):
    service_uuid = '1bc5d5a5-0200b89f-e6114d22-000da2cb'

    def __init__(self, bt_interface=None, timeout_secs=None):
        self.bt_interface = bt_interface
        self.timeout_secs = timeout_secs if timeout_secs else 2


    @classmethod
    def _get_uuids(cls, device):
        uuids = set()

        for id in device['uuids']:
            if isinstance(id, tuple):
                uuid = ''
                for i in range(0, len(id)):
                    token = struct.pack('<I', id[i])
                    for byte in token:
                        uuid += hex(byte)[2:].zfill(2)
                    uuid += ('-' if i < len(id)-1 else '')
                uuids.add(uuid)
            else:
                uuids.add(hex(id)[2:])

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
        'press' : '\x57\x01\x00',
        'on'    : '\x57\x01\x01',
        'off'   : '\x57\x01\x02',
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
    NOTE: since the interaction with the Switchbot requires root privileges
    (in order to scan on the bluetooth interface or setting gattlib in random),
    this plugin just wraps the module into a `sudo` flavor, since running
    Platypush with root privileges should be considered as a very bad idea.
    Make sure that your user has sudo privileges for running this bit of code.
    """

    def __init__(self, bt_interface=None, connect_timeout=None,
                 scan_timeout=None, devices={}, *args, **kwargs):
        self.bt_interface = bt_interface
        self.connect_timeout = connect_timeout if connect_timeout else 5
        self.scan_timeout = scan_timeout if scan_timeout else 2
        self.devices = devices


    def _run(self, device, command=None):
        output = None
        errors = []

        try:
            output = subprocess.check_output((
                'sudo python3 -m platypush.plugins.switch.switchbot ' +
                '--device {} ' +
                ('--interface {} '.format(self.bt_interface) if self.bt_interface else '') +
                ('--connect-timeout {} '.format(self.connect_timeout) if self.connect_timeout else '') +
                ('--{} '.format(command) if command else '')).format(device),
                stderr=subprocess.STDOUT, shell=True).decode('utf-8')
        except subprocess.CalledProcessError as e:
            errors = [e.output.decode('utf-8')]

        return Response(output=output, errors=errors)


    def press(self, device):
        return self._run(device)

    def on(self, device):
        return self._run(device, 'on')

    def off(self, device):
        return self._run(device, 'off')

    def scan(self):
        output = None
        errors = []

        try:
            print('sudo python3 -m platypush.plugins.switch.switchbot --scan ' +
                ('--interface {} '.format(self.bt_interface) if self.bt_interface else '') +
                ('--scan-timeout {} '.format(self.scan_timeout) if self.scan_timeout else ''))

            output = subprocess.check_output(
                'sudo python3 -m platypush.plugins.switch.switchbot --scan ' +
                ('--interface {} '.format(self.bt_interface) if self.bt_interface else '') +
                ('--scan-timeout {} '.format(self.scan_timeout) if self.scan_timeout else ''),
                stderr=subprocess.STDOUT, shell=True).decode('utf-8')
        except subprocess.CalledProcessError as e:
            errors = [e.output.decode('utf-8')]

        return Response(output=output, errors=errors)

# vim:sw=4:ts=4:et:

