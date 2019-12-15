import socket

from typing import Optional

from platypush.utils.workers import Worker
from .lib import WemoRunner


class ScanResult:
    def __init__(self, addr: str, name: str, on: bool):
        self.addr = addr
        self.name = name
        self.on = on


class Scanner(Worker):
    timeout = 1.5

    def __init__(self, port: int = WemoRunner.default_port, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.port = port

    def process(self, addr: str) -> Optional[ScanResult]:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            sock.connect((addr, self.port))
            sock.close()

            return ScanResult(addr=addr, name=WemoRunner.get_name(addr), on=WemoRunner.get_state(addr))
        except OSError:
            pass


# vim:sw=4:ts=4:et:
