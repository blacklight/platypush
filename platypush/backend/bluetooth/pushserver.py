import os

# noinspection PyPackageRequirements
from PyOBEX.server import PushServer

from platypush.backend.bluetooth import BluetoothBackend


class BluetoothPushserverBackend(BluetoothBackend, PushServer):
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
        BluetoothBackend.__init__(self, address=address, port=port, directory=directory,
                                  whitelisted_addresses=whitelisted_addresses, **kwargs)

    def run(self):
        if not os.path.isdir(self.directory):
            os.makedirs(self.directory, exist_ok=True)

        super().run()


# vim:sw=4:ts=4:et:
