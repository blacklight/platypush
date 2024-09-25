from dataclasses import dataclass, field
from socket import AddressFamily
from typing import List, Optional


@dataclass
class NetworkInterfaceAddress:
    """
    Network interface address data class.
    """

    family: Optional[AddressFamily] = None
    address: Optional[str] = None
    netmask: Optional[str] = None
    broadcast: Optional[str] = None


@dataclass
class NetworkInterface:
    """
    Network interface statistics data class.
    """

    interface: Optional[str] = None
    bytes_sent: int = 0
    bytes_recv: int = 0
    packets_sent: int = 0
    packets_recv: int = 0
    errors_in: int = 0
    errors_out: int = 0
    drop_in: int = 0
    drop_out: int = 0
    is_up: bool = False
    speed: int = 0
    mtu: int = 0
    duplex: Optional[str] = None
    flags: List[str] = field(default_factory=list)
    addresses: List[NetworkInterfaceAddress] = field(default_factory=list)
