import os
import stat

# noinspection PyPackageRequirements
from PyOBEX import requests, responses, headers
# noinspection PyPackageRequirements
from PyOBEX.server import BrowserServer

from platypush.backend.bluetooth import BluetoothBackend
from platypush.message.event.bluetooth import BluetoothFileGetRequestEvent


class BluetoothFileserverBackend(BluetoothBackend, BrowserServer):
    """
    Bluetooth OBEX file server.
    Enable it to allow bluetooth devices to browse files on this machine.

    If you run platypush as a non-root user (and you should) then you to change the group owner of the
    service discovery protocol file (/var/run/sdp) and add your user to that group. See
    `here <https://stackoverflow.com/questions/34599703/rfcomm-bluetooth-permission-denied-error-raspberry-pi>`_
    for details.

    Requires:

        * **pybluez** (``pip install pybluez``)
        * **pyobex** (``pip install git+https://github.com/BlackLight/PyOBEX``)

    """

    def __init__(self, port: int, address: str = '', directory: str = os.path.expanduser('~'),
                 whitelisted_addresses: list = None, **kwargs):
        """
        :param port: Bluetooth listen port
        :param address: Bluetooth address to bind the server to (default: any)
        :param directory: Directory to share (default: HOME directory)
        :param whitelisted_addresses: If set then only accept connections from the listed device addresses
        """
        BluetoothBackend.__init__(self, address=address, port=port, directory=directory,
                                  whitelisted_addresses=whitelisted_addresses, **kwargs)

        if not os.path.isdir(self.directory):
            raise FileNotFoundError(self.directory)

    def process_request(self, socket, request, *address):
        if isinstance(request, requests.Get):
            self.bus.post(BluetoothFileGetRequestEvent(address=address[0], port=address[1]))
            self.get(socket, request)
        else:
            super().process_request(socket, request, *address)

    def get(self, socket, request):
        name = ""
        req_type = ""

        for header in request.header_data:
            if isinstance(header, headers.Name):
                name = header.decode().strip("\x00")
                self.logger.info("Receiving request for {}".format(name))
            elif isinstance(header, headers.Type):
                req_type = header.decode().strip("\x00")
                self.logger.info("Request type: {}".format(req_type))

        path = os.path.abspath(os.path.join(self.directory, name))

        if os.path.isdir(path) or req_type == "x-obex/folder-listing":
            if path.startswith(self.directory):
                filelist = os.listdir(path)
                s = '<?xml version="1.0"?>\n<folder-listing>\n'

                for i in filelist:
                    objpath = os.path.join(path, i)
                    if os.path.isdir(objpath):
                        s += '  <folder name="{}" created="{}" />'.format(i, os.stat(objpath)[stat.ST_CTIME])
                    else:
                        s += '  <file name="{}" created="{}" size="{}" />'.format(
                            i, os.stat(objpath)[stat.ST_CTIME], os.stat(objpath)[stat.ST_SIZE])

                s += "</folder-listing>\n"
                self.logger.debug('Bluetooth get XML output:\n' + s)

                response = responses.Success()
                response_headers = [headers.Name(name.encode("utf8")),
                                    headers.Length(len(s)),
                                    headers.Body(s.encode("utf8"))]
                BrowserServer.send_response(self, socket, response, response_headers)
            else:
                self._reject(socket)
        else:
            self._reject(socket)


# vim:sw=4:ts=4:et:
