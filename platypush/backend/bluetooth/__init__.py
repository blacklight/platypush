import os
import time

# noinspection PyPackageRequirements
from PyOBEX import headers, requests, responses
# noinspection PyPackageRequirements
from PyOBEX.server import Server

from platypush.backend import Backend
from platypush.message.event.bluetooth import BluetoothDeviceConnectedEvent, BluetoothFileReceivedEvent, \
    BluetoothDeviceDisconnectedEvent, BluetoothFilePutRequestEvent


class BluetoothBackend(Backend, Server):
    _sleep_on_error = 10.0

    def __init__(self, address: str = '', port: int = None, directory: str = None, whitelisted_addresses=None,
                 **kwargs):
        Backend.__init__(self, **kwargs)
        Server.__init__(self, address=address)
        self.port = port
        self.directory = os.path.join(os.path.expanduser(directory))
        self.whitelisted_addresses = whitelisted_addresses or []
        self._sock = None

    def run(self):
        self.logger.info('Starting bluetooth service [address={}] [port={}]'.format(
            self.address, self.port))

        while not self.should_stop():
            try:
                # noinspection PyArgumentList
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
            Server.send_response(self, socket, responses.Continue())

            # Get the next part of the data.
            request = self.request_handler.decode(socket)

        Server.send_response(self, socket, responses.Success())
        name = os.path.basename(name.strip("\x00"))
        path = os.path.join(self.directory, name)

        self.logger.info("Writing file {}" .format(path))
        open(path, "wb").write(body.encode())
        self.bus.post(BluetoothFileReceivedEvent(path=path))

    def process_request(self, connection, request, *address):
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
