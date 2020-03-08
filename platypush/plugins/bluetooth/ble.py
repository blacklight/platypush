import base64
import os
import subprocess
import sys
import time
from typing import Optional, Dict

from platypush.plugins import action
from platypush.plugins.sensor import SensorPlugin
from platypush.message.response.bluetooth import BluetoothScanResponse, BluetoothDiscoverPrimaryResponse, \
    BluetoothDiscoverCharacteristicsResponse


class BluetoothBlePlugin(SensorPlugin):
    """
    Bluetooth BLE (low-energy) plugin

    Requires:

        * **pybluez** (``pip install pybluez``)
        * **gattlib** (``pip install gattlib``)

    Note that the support for bluetooth low-energy devices on Linux requires:

        * A bluetooth adapter compatible with the bluetooth 5.0 specification or higher;
        * To run platypush with root privileges (which is usually a very bad idea), or to set the raw net
          capabilities on the Python executable (which is also a bad idea, because any Python script will
          be able to access the kernel raw network API, but it's probably better than running a network
          server that can execute system commands as root user). If you don't want to set special permissions
          on the main Python executable and you want to run the bluetooth LTE plugin then the advised approach
          is to install platypush in a virtual environment and set the capabilities on the venv python executable,
          or run your platypush instance in Docker.

          You can set the capabilities on the Python executable through the following shell command::

            [sudo] setcap 'cap_net_raw,cap_net_admin+eip' /path/to/your/python

    """

    def __init__(self, interface: str = 'hci0', **kwargs):
        """
        :param interface: Default adapter device to be used (default: 'hci0')
        """
        super().__init__(**kwargs)
        self.interface = interface
        self._req_by_addr = {}

    @staticmethod
    def _get_python_interpreter() -> str:
        exe = sys.executable

        while os.path.islink(exe):
            target = os.readlink(exe)
            if not os.path.isabs(target):
                target = os.path.abspath(os.path.join(os.path.dirname(exe), target))
            exe = target

        return exe

    @staticmethod
    def _python_has_ble_capabilities(exe: str) -> bool:
        getcap = subprocess.Popen(['getcap', exe], stdout=subprocess.PIPE)
        output = getcap.communicate()[0].decode().split('\n')
        if not output:
            return False

        caps = set(output.pop(0).split('=').pop().strip().split(','))
        return 'cap_net_raw+eip' in caps and 'cap_net_admin' in caps

    def _check_ble_support(self):
        # Check if the script is running as root or if the Python executable
        # has 'cap_net_admin,cap_net_raw+eip' capabilities
        exe = self._get_python_interpreter()
        if os.getuid() != 0 and not self._python_has_ble_capabilities(exe):
            raise RuntimeError('You are not running platypush as root and the Python interpreter has no ' +
                               'capabilities/permissions to access the BLE stack. Set the permissions on ' +
                               'your Python interpreter through:\n' +
                               '\t[sudo] setcap "cap_net_raw,cap_net_admin+eip" {}'.format(exe))

    @action
    def scan(self, interface: Optional[str] = None, duration: int = 10) -> BluetoothScanResponse:
        """
        Scan for nearby bluetooth low-energy devices

        :param interface: Bluetooth adapter name to use (default configured if None)
        :param duration: Scan duration in seconds
        """
        from bluetooth.ble import DiscoveryService

        if interface is None:
            interface = self.interface

        self._check_ble_support()
        svc = DiscoveryService(interface)
        devices = svc.discover(duration)
        return BluetoothScanResponse(devices)

    @action
    def get_measurement(self, interface: Optional[str] = None, duration: Optional[int] = 10, *args, **kwargs) \
            -> Dict[str, dict]:
        """
        Wrapper for ``scan`` that returns bluetooth devices in a format usable by sensor backends.

        :param interface: Bluetooth adapter name to use (default configured if None)
        :param duration: Scan duration in seconds
        :return: Device address -> info map.
        """
        devices = self.scan(interface=interface, duration=duration).output
        return {device['addr']: device for device in devices}

    # noinspection PyArgumentList
    @action
    def connect(self, device: str, interface: str = None, wait: bool = True, channel_type: str = 'public',
                security_level: str = 'low', psm: int = 0, mtu: int = 0, timeout: float = 10.0):
        """
        Connect to a bluetooth LE device

        :param device: Device address to connect to
        :param interface: Bluetooth adapter name to use (default configured if None)
        :param wait: If True then wait for the connection to be established before returning (no timeout)
        :param channel_type: Channel type, usually 'public' or 'random'
        :param security_level: Security level - possible values: ['low', 'medium', 'high']
        :param psm: PSM value (default: 0)
        :param mtu: MTU value (default: 0)
        :param timeout: Connection timeout if wait is not set (default: 10 seconds)
        """
        from gattlib import GATTRequester

        req = self._req_by_addr.get(device)
        if req:
            if req.is_connected():
                self.logger.info('Device {} is already connected'.format(device))
                return

            self._req_by_addr[device] = None

        if not interface:
            interface = self.interface
        if interface:
            req = GATTRequester(device, False, interface)
        else:
            req = GATTRequester(device, False)

        self.logger.info('Connecting to {}'.format(device))
        connect_start_time = time.time()
        req.connect(wait, channel_type, security_level, psm, mtu)

        if not wait:
            while not req.is_connected():
                if time.time() - connect_start_time > timeout:
                    raise TimeoutError('Connection to {} timed out'.format(device))
                time.sleep(0.1)

        self.logger.info('Connected to {}'.format(device))
        self._req_by_addr[device] = req

    @action
    def read(self, device: str, interface: str = None, uuid: str = None, handle: int = None,
             binary: bool = False, disconnect_on_recv: bool = True, **kwargs) -> str:
        """
        Read a message from a device

        :param device: Device address to connect to
        :param interface: Bluetooth adapter name to use (default configured if None)
        :param uuid: Service UUID. Either the UUID or the device handle must be specified
        :param handle: Device handle. Either the UUID or the device handle must be specified
        :param binary: Set to true to return data as a base64-encoded binary string
        :param disconnect_on_recv: If True (default) disconnect when the response is received
        :param kwargs: Extra arguments to be passed to :meth:`connect`
        """
        if interface is None:
            interface = self.interface
        if not (uuid or handle):
            raise AttributeError('Specify either uuid or handle')

        self.connect(device, interface=interface, **kwargs)
        req = self._req_by_addr[device]

        if uuid:
            data = req.read_by_uuid(uuid)[0]
        else:
            data = req.read_by_handle(handle)[0]

        if binary:
            data = base64.encodebytes(data.encode() if isinstance(data, str) else data).decode().strip()
        if disconnect_on_recv:
            self.disconnect(device)

        return data

    @action
    def write(self, device: str, data, handle: int = None, interface: str = None, binary: bool = False,
              disconnect_on_recv: bool = True, **kwargs) -> str:
        """
        Writes data to a device

        :param device: Device address to connect to
        :param data: Data to be written (str or bytes)
        :param interface: Bluetooth adapter name to use (default configured if None)
        :param handle: Device handle. Either the UUID or the device handle must be specified
        :param binary: Set to true if data is a base64-encoded binary string
        :param disconnect_on_recv: If True (default) disconnect when the response is received
        :param kwargs: Extra arguments to be passed to :meth:`connect`
        """
        if interface is None:
            interface = self.interface
        if binary:
            data = base64.decodebytes(data.encode() if isinstance(data, str) else data)

        self.connect(device, interface=interface, **kwargs)
        req = self._req_by_addr[device]

        data = req.write_by_handle(handle, data)[0]

        if binary:
            data = base64.encodebytes(data.encode() if isinstance(data, str) else data).decode().strip()
        if disconnect_on_recv:
            self.disconnect(device)

        return data

    @action
    def disconnect(self, device: str):
        """
        Disconnect from a connected device

        :param device: Device address
        """
        req = self._req_by_addr.get(device)
        if not req:
            self.logger.info('Device {} not connected'.format(device))

        req.disconnect()
        self.logger.info('Device {} disconnected'.format(device))

    @action
    def discover_primary(self, device: str, interface: str = None, **kwargs) -> BluetoothDiscoverPrimaryResponse:
        """
        Discover the primary services advertised by a LE bluetooth device

        :param device: Device address to connect to
        :param interface: Bluetooth adapter name to use (default configured if None)
        :param kwargs: Extra arguments to be passed to :meth:`connect`
        """
        if interface is None:
            interface = self.interface

        self.connect(device, interface=interface, **kwargs)
        req = self._req_by_addr[device]
        services = req.discover_primary()
        self.disconnect(device)
        return BluetoothDiscoverPrimaryResponse(services=services)

    @action
    def discover_characteristics(self, device: str, interface: str = None, **kwargs) \
            -> BluetoothDiscoverCharacteristicsResponse:
        """
        Discover the characteristics of a LE bluetooth device

        :param device: Device address to connect to
        :param interface: Bluetooth adapter name to use (default configured if None)
        :param kwargs: Extra arguments to be passed to :meth:`connect`
        """
        if interface is None:
            interface = self.interface

        self.connect(device, interface=interface, **kwargs)
        req = self._req_by_addr[device]
        characteristics = req.discover_characteristics()
        self.disconnect(device)
        return BluetoothDiscoverCharacteristicsResponse(characteristics=characteristics)


# vim:sw=4:ts=4:et:
