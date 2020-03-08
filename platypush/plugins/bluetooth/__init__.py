import base64
import os
import re
import select

from typing import Dict, Optional

from platypush.plugins.sensor import SensorPlugin

from platypush.plugins import action
from platypush.message.response.bluetooth import BluetoothScanResponse, \
    BluetoothLookupNameResponse, BluetoothLookupServiceResponse, BluetoothResponse


class BluetoothPlugin(SensorPlugin):
    """
    Bluetooth plugin

    Requires:

        * **pybluez** (``pip install pybluez``)
        * **pyobex** (``pip install git+https://github.com/BlackLight/PyOBEX``)

    """

    import bluetooth

    class _DeviceDiscoverer(bluetooth.DeviceDiscoverer):
        def __init__(self, name, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.name = name
            self.device = {}
            self.done = True

        def pre_inquiry(self):
            self.done = False

        def device_discovered(self, dev_addr, dev_class, rssi, dev_name):
            dev_name = dev_name.decode()
            if dev_name == self.name:
                self.device = {
                    'addr': dev_addr,
                    'name': dev_name,
                    'class': dev_class,
                }

                self.done = True

        def inquiry_complete(self):
            self.done = True

    def __init__(self, device_id: int = -1, **kwargs):
        """
        :param device_id: Default adapter device_id to be used (default: -1, auto)
        """
        super().__init__(**kwargs)
        self.device_id = device_id
        self._devices = []
        self._devices_by_addr = {}
        self._devices_by_name = {}
        self._port_and_protocol_by_addr_and_srv_uuid = {}
        self._port_and_protocol_by_addr_and_srv_name = {}
        self._socks = {}

    def _get_device_addr(self, device):
        if re.match('([0-9A-F]{2}:){5}[0-9A-F]{2}', device, re.IGNORECASE):
            return device
        if device in self._devices_by_name:
            return self._devices_by_name[device]['addr']

        return self.lookup_address(device).output['addr']

    @action
    def scan(self, device_id: Optional[int] = None, duration: int = 10) -> BluetoothScanResponse:
        """
        Scan for nearby bluetooth devices

        :param device_id: Bluetooth adapter ID to use (default configured if None)
        :param duration: Scan duration in seconds
        """
        from bluetooth import discover_devices

        if device_id is None:
            device_id = self.device_id

        self.logger.debug('Discovering devices on adapter {}, duration: {} seconds'.format(
            device_id, duration))

        devices = discover_devices(duration=duration, lookup_names=True, lookup_class=True, device_id=device_id,
                                   flush_cache=True)
        response = BluetoothScanResponse(devices)

        self._devices = response.devices
        self._devices_by_addr = {dev['addr']: dev for dev in self._devices}
        self._devices_by_name = {dev['name']: dev for dev in self._devices if dev.get('name')}
        return response

    @action
    def get_measurement(self, device_id: Optional[int] = None, duration: Optional[int] = 10, *args, **kwargs) \
            -> Dict[str, dict]:
        """
        Wrapper for ``scan`` that returns bluetooth devices in a format usable by sensor backends.

        :param device_id: Bluetooth adapter ID to use (default configured if None)
        :param duration: Scan duration in seconds
        :return: Device address -> info map.
        """
        devices = self.scan(device_id=device_id, duration=duration).output
        return {device['addr']: device for device in devices}

    @action
    def lookup_name(self, addr: str, timeout: int = 10) -> BluetoothLookupNameResponse:
        """
        Look up the name of a nearby bluetooth device given the address

        :param addr: Device address
        :param timeout: Lookup timeout (default: 10 seconds)
        """
        from bluetooth import lookup_name

        self.logger.info('Looking up name for device {}'.format(addr))
        name = lookup_name(addr, timeout=timeout)

        dev = {
            'addr': addr,
            'name': name,
            'class': self._devices_by_addr.get(addr, {}).get('class'),
        }

        self._devices_by_addr[addr] = dev
        if name:
            self._devices_by_name[name] = dev

        return BluetoothLookupNameResponse(addr=addr, name=name)

    @action
    def lookup_address(self, name: str, timeout: int = 10) -> BluetoothLookupNameResponse:
        """
        Look up the address of a nearby bluetooth device given the name

        :param name: Device name
        :param timeout: Lookup timeout (default: 10 seconds)
        """

        self.logger.info('Looking up address for device {}'.format(name))
        discoverer = self._DeviceDiscoverer(name)
        discoverer.find_devices(lookup_names=True, duration=timeout)
        readfiles = [discoverer]

        while True:
            rfds = select.select(readfiles, [], [])[0]
            if discoverer in rfds:
                discoverer.process_event()

            if discoverer.done:
                break

        dev = discoverer.device
        if not dev:
            raise RuntimeError('No such device: {}'.format(name))

        addr = dev.get('addr')
        self._devices_by_addr[addr] = dev
        self._devices_by_name[name] = dev
        return BluetoothLookupNameResponse(addr=addr, name=name)

    @action
    def find_service(self, name: str = None, addr: str = None, uuid: str = None) -> BluetoothLookupServiceResponse:
        """
        Look up for a service published by a nearby bluetooth device. If all the parameters are null then all the
        published services on the nearby devices will be returned. See
        `:class:platypush.message.response.bluetoothBluetoothLookupServiceResponse` for response structure reference.

        :param name: Service name
        :param addr: Service/device address
        :param uuid: Service UUID
        """

        import bluetooth
        from bluetooth import find_service
        services = find_service(name=name, address=addr, uuid=uuid)

        self._port_and_protocol_by_addr_and_srv_uuid.update({
            (srv['host'], srv['service-id']): (srv['port'], getattr(bluetooth, srv['protocol']))
            for srv in services if srv.get('service-id')
        })

        self._port_and_protocol_by_addr_and_srv_name.update({
            (srv['host'], srv['name']): (srv['port'], getattr(bluetooth, srv['protocol']))
            for srv in services if srv.get('name')
        })

        return BluetoothLookupServiceResponse(services)

    def _get_sock(self, protocol=None, device: str = None, port: int = None, service_uuid: str = None,
                  service_name: str = None, connect_if_closed=False):
        sock = None
        addr = self._get_device_addr(device)

        if not (addr and port and protocol):
            addr, port, protocol = self._get_addr_port_protocol(protocol=protocol, device=device, port=port,
                                                                service_uuid=service_uuid, service_name=service_name)

        if (addr, port) in self._socks:
            sock = self._socks[(addr, port)]
        elif connect_if_closed:
            self.connect(protocol=protocol, device=device, port=port, service_uuid=service_uuid,
                         service_name=service_name)
            sock = self._socks[(addr, port)]

        return sock

    def _get_addr_port_protocol(self, protocol=None, device: str = None, port: int = None, service_uuid: str = None,
                                service_name: str = None) -> tuple:
        import bluetooth

        addr = self._get_device_addr(device) if device else None
        if service_uuid or service_name:
            if addr:
                if service_uuid:
                    (port, protocol) = self._port_and_protocol_by_addr_and_srv_uuid[(addr, service_uuid)] \
                        if (addr, service_uuid) in self._port_and_protocol_by_addr_and_srv_uuid else \
                        (None, None)
                else:
                    (port, protocol) = self._port_and_protocol_by_addr_and_srv_name[(addr, service_name)] \
                        if (addr, service_name) in self._port_and_protocol_by_addr_and_srv_name else \
                        (None, None)

            if not (addr and port):
                self.logger.info('Discovering devices, service_name={name}, uuid={uuid}, address={addr}'.format(
                    name=service_name, uuid=service_uuid, addr=addr))

                services = [
                    srv for srv in self.find_service().services
                    if (service_name is None or srv.get('name') == service_name) and
                       (addr is None or srv.get('host') == addr) and
                       (service_uuid is None or srv.get('service-id') == service_uuid)
                ]

                if not services:
                    raise RuntimeError('No such service: name={name} uuid={uuid} address={addr}'.format(
                        name=service_name, uuid=service_uuid, addr=addr))

                service = services[0]
                addr = service['host']
                port = service['port']
                protocol = getattr(bluetooth, service['protocol'])
        elif protocol:
            if isinstance(protocol, str):
                protocol = getattr(bluetooth, protocol)
        else:
            raise RuntimeError('No service name/UUID nor bluetooth protocol (RFCOMM/L2CAP) specified')

        if not (addr and port):
            raise RuntimeError('No valid device name/address, port, service name or UUID specified')

        return addr, port, protocol

    @action
    def connect(self, protocol=None, device: str = None, port: int = None, service_uuid: str = None,
                service_name: str = None):
        """
        Connect to a bluetooth device.
        You can query the advertised services through ``find_service``.

        :param protocol: Supported values: either 'RFCOMM'/'L2CAP' (str) or bluetooth.RFCOMM/bluetooth.L2CAP
            int constants (int)
        :param device: Device address or name
        :param port: Port number
        :param service_uuid: Service UUID
        :param service_name: Service name
        """
        from bluetooth import BluetoothSocket

        addr, port, protocol = self._get_addr_port_protocol(protocol=protocol, device=device, port=port,
                                                            service_uuid=service_uuid, service_name=service_name)
        sock = self._get_sock(protocol=protocol, device=addr, port=port)
        if sock:
            self.close(device=addr, port=port)

        sock = BluetoothSocket(protocol)
        self.logger.info('Opening connection to device {} on port {}'.format(addr, port))
        sock.connect((addr, port))
        self.logger.info('Connected to device {} on port {}'.format(addr, port))
        self._socks[(addr, port)] = sock

    @action
    def close(self, device: str = None, port: int = None, service_uuid: str = None, service_name: str = None):
        """
        Close an active bluetooth connection

        :param device: Device address or name
        :param port: Port number
        :param service_uuid: Service UUID
        :param service_name: Service name
        """
        sock = self._get_sock(device=device, port=port, service_uuid=service_uuid, service_name=service_name)

        if not sock:
            self.logger.debug('Close on device {}({}) that is not connected'.format(device, port))
            return

        try:
            sock.close()
        except Exception as e:
            self.logger.warning('Exception while closing previous connection to {}({}): {}'.format(
                device, port, str(e)))

    @action
    def send(self, data, device: str = None, port: int = None, service_uuid: str = None, service_name: str = None,
             binary: bool = False):
        """
        Send data to an active bluetooth connection

        :param data: Data to be sent
        :param device: Device address or name
        :param service_uuid: Service UUID
        :param service_name: Service name
        :param port: Port number
        :param binary: Set to true if msg is a base64-encoded binary string
        """
        from bluetooth import BluetoothError

        sock = self._get_sock(device=device, port=port, service_uuid=service_uuid, service_name=service_name,
                              connect_if_closed=True)

        if binary:
            data = base64.decodebytes(data.encode() if isinstance(data, str) else data)

        try:
            sock.send(data)
        except BluetoothError as e:
            self.close(device=device, port=port, service_uuid=service_uuid, service_name=service_name)
            raise e

    @action
    def recv(self, device: str, port: int, service_uuid: str = None, service_name: str = None, size: int = 1024,
             binary: bool = False) -> BluetoothResponse:
        """
        Send data to an active bluetooth connection

        :param device: Device address or name
        :param port: Port number
        :param service_uuid: Service UUID
        :param service_name: Service name
        :param size: Maximum number of bytes to be read
        :param binary: Set to true to return a base64-encoded binary string
        """
        from bluetooth import BluetoothError

        sock = self._get_sock(device=device, port=port, service_uuid=service_uuid, service_name=service_name,
                              connect_if_closed=True)

        if not sock:
            self.connect(device=device, port=port, service_uuid=service_uuid, service_name=service_name)
            sock = self._get_sock(device=device, port=port, service_uuid=service_uuid, service_name=service_name)

        try:
            data = sock.recv(size)
        except BluetoothError as e:
            self.close(device=device, port=port, service_uuid=service_uuid, service_name=service_name)
            raise e

        if binary:
            data = base64.encodebytes(data)

        return BluetoothResponse(output=data.decode())

    @action
    def set_l2cap_mtu(self, mtu: int, device: str = None, port: int = None, service_name: str = None,
                      service_uuid: str = None):
        """
        Set the L2CAP MTU (Maximum Transmission Unit) value for a connected bluetooth device.
        Both the devices usually use the same MTU value over a connection.

        :param device: Device address or name
        :param port: Port number
        :param service_uuid: Service UUID
        :param service_name: Service name
        :param mtu: New MTU value
        """
        from bluetooth import BluetoothError, set_l2cap_mtu, L2CAP

        sock = self._get_sock(protocol=L2CAP, device=device, port=port, service_uuid=service_uuid,
                              service_name=service_name, connect_if_closed=True)

        if not sock:
            raise RuntimeError('set_l2cap_mtu: device not connected')

        try:
            set_l2cap_mtu(sock, mtu)
        except BluetoothError as e:
            self.close(device=device, port=port, service_name=service_name, service_uuid=service_uuid)
            raise e

    @action
    def send_file(self, filename: str, device: str, port: int = None, data=None, service_name='OBEX Object Push',
                  binary: bool = False):
        """
        Send a local file to a device that exposes an OBEX Object Push service

        :param filename: Path of the file to be sent
        :param data: Alternatively to a file on disk you can send raw (string or binary) content
        :param device: Device address or name
        :param port: Port number
        :param service_name: Service name
        :param binary: Set to true if data is a base64-encoded binary string
        """
        from PyOBEX.client import Client

        if not data:
            filename = os.path.abspath(os.path.expanduser(filename))
            with open(filename, 'r') as f:
                data = f.read()
            filename = os.path.basename(filename)
        else:
            if binary:
                data = base64.decodebytes(data.encode() if isinstance(data, str) else data)

        addr, port, protocol = self._get_addr_port_protocol(device=device, port=port,
                                                            service_name=service_name)

        client = Client(addr, port)
        self.logger.info('Connecting to device {}'.format(addr))
        client.connect()
        self.logger.info('Sending file {} to device {}'.format(filename, addr))
        client.put(filename, data)
        self.logger.info('File {} sent to device {}'.format(filename, addr))
        client.disconnect()


# vim:sw=4:ts=4:et:
