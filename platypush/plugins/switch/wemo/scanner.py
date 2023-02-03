import socket

from dataclasses import dataclass
from typing import Optional

from platypush.utils.workers import Worker
from .lib import WemoRunner


@dataclass
class ScanResult:
    """
    Models a scan result.
    """

    addr: str
    name: str
    on: bool


class Scanner(Worker):
    """
    Worker class used to scan WeMo devices on the network.
    """

    timeout = 1.5

    def __init__(self, *args, port: int = WemoRunner.default_port, **kwargs):
        super().__init__(*args, **kwargs)
        self.port = port

    def process(self, msg: str) -> Optional[ScanResult]:
        addr = msg

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            sock.connect((addr, self.port))
            sock.close()

            return ScanResult(
                addr=addr, name=WemoRunner.get_name(addr), on=WemoRunner.get_state(addr)
            )
        except OSError:
            return None


# vim:sw=4:ts=4:et:
