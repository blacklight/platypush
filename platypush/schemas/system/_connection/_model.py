from dataclasses import dataclass, field
from socket import AddressFamily, SocketKind
from typing import Optional


@dataclass
class Connection:
    """
    Network/UNIX socket data class.
    """

    fd: int = field(
        metadata={
            'metadata': {
                'description': 'File descriptor',
                'example': 3,
            },
        }
    )

    family: AddressFamily = field(
        metadata={
            'metadata': {
                'description': 'Socket family',
                'example': AddressFamily.AF_INET.name,
            }
        }
    )

    type: SocketKind = field(
        metadata={
            'metadata': {
                'description': 'Socket type',
                'example': SocketKind.SOCK_STREAM.name,
            }
        }
    )

    local_address: str = field(
        metadata={
            'metadata': {
                'description': 'Local address, as an IP address for network '
                'connections and a socket path for a UNIX socket',
                'example': '192.168.1.2',
            }
        }
    )

    local_port: Optional[int] = field(
        metadata={
            'metadata': {
                'description': 'Local port, if this is a TCP/UDP connection, '
                'otherwise null',
                'example': 12345,
            }
        }
    )

    remote_address: Optional[str] = field(
        metadata={
            'metadata': {
                'description': 'Remote address, if this is a network '
                'connection, otherwise null',
                'example': '192.168.1.1',
            }
        }
    )

    remote_port: Optional[int] = field(
        metadata={
            'metadata': {
                'description': 'Local port, if this is a TCP/UDP connection, '
                'otherwise null',
                'example': 443,
            }
        }
    )

    status: Optional[str] = field(
        metadata={
            'metadata': {
                'description': 'Connection status, if this is a network '
                'connection, otherise null',
                'example': 'ESTABLISHED',
            }
        }
    )

    pid: Optional[int] = field(
        metadata={
            'metadata': {
                'description': 'ID of the process that owns the connection',
                'example': 4321,
            }
        }
    )
