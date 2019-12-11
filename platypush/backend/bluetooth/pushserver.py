import os
import time

# noinspection PyPackageRequirements
from PyOBEX import headers, requests, responses, server

from platypush.backend import Backend
from platypush.message.event.bluetooth import BluetoothDeviceConnectedEvent, BluetoothFileReceivedEvent, \
    BluetoothDeviceDisconnectedEvent, BluetoothFilePutRequestEvent


class BluetoothPushserverBackend(Backend, server.PushServer):
    """
    Bluetooth OBEX push server.
    Enable it to allow bluetooth file transfers from other devices.

    If you run platypush as a non-root user (and you should) then you to change the group owner of the
    service discovery protocol file (/var/run/sdp) and add your user to that group. See
    `here <https://stackoverflow.com/questions/34599703/rfcomm-bluetooth-permission-denied-error-raspberry-pi>`_
    for details.

    Requires:

        * **pybluez** (``pip install pybluez``)
        * **pyobex** (``pip install git+https://github.com/BlackLight/PyOBEX``)

    """

    _sleep_on_error = 10.0

    def __init__(self, port: int, address: str = '',
                 directory: str = os.path.join(os.path.expanduser('~'), 'bluetooth'),
                 whitelisted_addresses: list = None, **kwargs):
        """
        :param port: Bluetooth listen port
        :param address: Bluetooth address to bind the server to (default: any)
        :param directory: Destination directory where files will be downloaded (default: ~/bluetooth)
        :param whitelisted_addresses: If set then only accept connections from the listed device addresses
        """
        Backend.__init__(self, **kwargs)
        server.PushServer.__init__(self, address=address)

        self.port = port
        self.directory = os.path.join(os.path.expanduser(directory))
        self.whitelisted_addresses = whitelisted_addresses or []
        self._sock = None

    def run(self):
        super().run()

        if not os.path.isdir(self.directory):
            os.makedirs(self.directory, exist_ok=True)

        self.logger.info('Started bluetooth push service [address={}] [port={}]'.format(
            self.address, self.port))

        while not self.should_stop():
            try:
                self._sock = self.start_service(self.port)
                self.serve(self._sock)
            except Exception as e:
                self.logger.error('Error on bluetooth connection [address={}] [port={}]: {}'.format(
                    self.address, self.port, str(e)))
                time.sleep(self._sleep_on_error)
            finally:
                self.stop()

    def stop(self):
        if self._sock:
            self.stop_service(self._sock)
        self._sock = None

    def put(self, socket, request):
        name = ""
        body = ""

        while True:
            for header in request.header_data:
                if isinstance(header, headers.Name):
                    name = header.decode()
                    self.logger.info("Receiving {}".format(name))
                elif isinstance(header, headers.Length):
                    length = header.decode()
                    self.logger.info("Content length: {} bytes".format(length))
                elif isinstance(header, headers.Body):
                    body += header.decode()
                elif isinstance(header, headers.End_Of_Body):
                    body += header.decode()

            if request.is_final():
                break

            # Ask for more data.
            self.send_response(socket, responses.Continue())

            # Get the next part of the data.
            request = self.request_handler.decode(socket)

        self.send_response(socket, responses.Success())
        name = os.path.basename(name.strip("\x00"))
        path = os.path.join(self.directory, name)

        self.logger.info("Writing file {}" .format(path))
        open(path, "wb").write(body.encode())
        self.bus.post(BluetoothFileReceivedEvent(path=path))

    def process_request(self, connection, request, *address):
        """Processes the request from the connection.

        This method should be reimplemented in subclasses to add support for
        more request types.
        """

        if isinstance(request, requests.Connect):
            self.connect(connection, request)
            self.bus.post(BluetoothDeviceConnectedEvent(address=address[0], port=address[1]))
        elif isinstance(request, requests.Disconnect):
            self.disconnect(connection)
            self.bus.post(BluetoothDeviceDisconnectedEvent(address=address[0], port=address[1]))
        elif isinstance(request, requests.Put):
            self.bus.post(BluetoothFilePutRequestEvent(address=address[0], port=address[1]))
            self.put(connection, request)
        else:
            self._reject(connection)
            self.bus.post(BluetoothFilePutRequestEvent(address=address[0], port=address[1]))

    def accept_connection(self, address, port):
        return address in self.whitelisted_addresses


# vim:sw=4:ts=4:et:
