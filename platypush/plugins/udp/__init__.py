import base64
import json
import socket

from typing import Optional, Union

from platypush.plugins import Plugin, action


class UdpPlugin(Plugin):
    """
    Plugin for raw UDP communications.
    """

    @action
    def send(self, data: Union[bytes, str], host: str, port: int, binary: bool = False,
             timeout: Optional[float] = None, recv_response: bool = False, **recv_opts):
        """
        Send data over a UDP connection.

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

        sd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if timeout:
            sd.settimeout(timeout)

        sd.sendto(data, (host, port))
        if not recv_response:
            return

        recv_opts.update({
            'host': host,
            'port': port,
            'timeout': timeout,
            'binary': binary,
        })

        data = sd.recvfrom(**recv_opts)
        if binary:
            data = base64.encodebytes(data)
        data = data.decode()
        return data


# vim:sw=4:ts=4:et:
