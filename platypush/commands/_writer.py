from logging import getLogger
from socket import socket

from platypush.commands import Command


# pylint: disable=too-few-public-methods
class CommandWriter:
    """
    Writes command objects to file-like I/O objects.
    """

    def __init__(self):
        self.logger = getLogger(__name__)

    def write(self, cmd: Command, sock: socket):
        """
        Writes a command to a file-like I/O object.

        :param cmd: The command to write.
        :param fp: The file-like I/O object to write to.
        """

        buf = cmd.to_bytes()
        sock.sendall(buf)
