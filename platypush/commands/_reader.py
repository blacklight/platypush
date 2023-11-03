from logging import getLogger
from socket import socket
from typing import Optional

from platypush.commands import Command


# pylint: disable=too-few-public-methods
class CommandReader:
    """
    Reads command objects from file-like I/O objects.
    """

    _max_bufsize = 8192
    """Maximum size of a command that can be queued in the stream."""

    _bufsize = 1024
    """Size of the buffer used to read commands from the socket."""

    def __init__(self):
        self.logger = getLogger(__name__)
        self._buf = bytes()

    def _parse_command(self, data: bytes) -> Optional[Command]:
        """
        Parses a command from the received data.

        :param data: Data received from the socket
        :return: The parsed command
        """
        try:
            return Command.parse(data)
        except ValueError as e:
            self.logger.warning('Error while parsing command: %s', e)
            return None

    def read(self, sock: socket) -> Optional[Command]:
        """
        Parses the next command from the file-like I/O object.

        :param fp: The file-like I/O object to read from.
        :return: The parsed command.
        """
        try:
            data = sock.recv(self._bufsize)
        except OSError as e:
            self.logger.warning(
                'Error while reading from socket %s: %s', sock.getsockname(), e
            )
            return None

        for ch in data:
            if bytes([ch]) == Command.END_OF_COMMAND:
                cmd = self._parse_command(self._buf)
                self._buf = bytes()

                if cmd:
                    return cmd
            elif len(self._buf) >= self._max_bufsize:
                self.logger.warning(
                    'The received command is too long: length=%d', len(self._buf)
                )

                self._buf = bytes()
                break
            else:
                self._buf += bytes([ch])

        return None
