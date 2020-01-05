import base64
import json
import socket

from typing import Optional, Union

from platypush.plugins import Plugin, action


class TcpPlugin(Plugin):
    """
    Plugin for raw TCP communications.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._sockets = {}

    def _connect(self, host: str, port: int, timeout: Optional[float] = None) -> socket.socket:
        sd = self._sockets.get((host, port))
        if sd:
            return sd

        sd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if timeout:
            sd.settimeout(timeout)
        sd.connect((host, port))
        self._sockets[(host, port)] = sd
        return sd

    @action
    def connect(self, host: str, port: int, timeout: Optional[float] = None):
        """
        Open a TCP connection.

        :param host: Host IP/name.
        :param port: TCP port.
        :param timeout: Connection timeout in seconds (default: None).
        """
        self._connect(host, port, timeout)

    @action
    def close(self, host: str, port: int):
        """
        Close an active TCP connection.

        :param host: Host IP/name.
        :param port: TCP port.
        """
        sd = self._sockets.get((host, port))
        if not sd:
            self.logger.warning('Not connected to ({}, {})'.format(host, port))
            return

        sd.close()

    @action
    def send(self, data: Union[bytes, str], host: str, port: int, binary: bool = False,
             timeout: Optional[float] = None, recv_response: bool = False, **recv_opts):
        """
        Send data over a TCP connection. If the connection isn't active it will be created.

        :param data: Data to be sent, as bytes or string.
        :param host: Host IP/name.
        :param port: TCP port.
        :param binary: If set to True and ``data`` is a string then will be treated as base64-encoded binary input.
        :param timeout: Connection timeout in seconds (default: None).
        :param recv_response: If True then the action will wait for a response from the server before closing the
            connection. Note that ``recv_opts`` must be specified in this case - at least ``length``.
        """
        if isinstance(data, list) or isinstance(data, dict):
            data = json.dumps(data)
        if isinstance(data, str):
            data = data.encode()
            if binary:
                data = base64.decodebytes(data)

        sd = self._connect(host, port, timeout)

        try:
            sd.send(data)
            if recv_response:
                recv_opts.update({
                    'host': host,
                    'port': port,
                    'timeout': timeout,
                    'binary': binary,
                })

                return self.recv(**recv_opts)
        finally:
            self.close(host, port)

    @action
    def recv(self, length: int, host: str, port: int, binary: bool = False, timeout: Optional[float] = None) -> str:
        """
        Receive data from a TCP connection. If the connection isn't active it will be created.

        :param length: Maximum number of bytes to be received.
        :param host: Host IP/name.
        :param port: TCP port.
        :param binary: If set to True then the output will be base64-encoded, otherwise decoded as string.
        :param timeout: Connection timeout in seconds (default: None).
        """
        sd = self._connect(host, port, timeout)

        try:
            data = sd.recv(length)
            if binary:
                data = base64.encodebytes(data).decode()
            else:
                data = data.decode()

            return data
        finally:
            self.close(host, port)


# vim:sw=4:ts=4:et:
