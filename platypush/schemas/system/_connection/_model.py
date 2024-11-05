from dataclasses import dataclass
from socket import AddressFamily, SocketKind
from typing import Optional


@dataclass
class Connection:
    """
    Network/UNIX socket data class.
    """

    fd: int
    family: AddressFamily
    type: SocketKind
    local_address: str
    local_port: Optional[int] = None
    remote_address: Optional[str] = None
    remote_port: Optional[int] = None
    status: Optional[str] = None
    pid: Optional[int] = None
