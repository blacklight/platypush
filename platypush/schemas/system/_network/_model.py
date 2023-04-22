from dataclasses import dataclass, field
from socket import AddressFamily
from typing import List, Optional


@dataclass
class NetworkInterface:
    """
    Network interface statistics data class.
    """

    interface: Optional[str] = field(
        metadata={
            'metadata': {
                'description': 'Network interface identifier',
                'example': 'eth0',
            }
        }
    )

    bytes_sent: int = field(
        metadata={
            'metadata': {
                'description': 'Number of bytes sent',
            }
        }
    )

    bytes_recv: int = field(
        metadata={
            'metadata': {
                'description': 'Number of bytes received',
            }
        }
    )

    packets_sent: int = field(
        metadata={
            'metadata': {
                'description': 'Number of packets sent',
            }
        }
    )

    packets_recv: int = field(
        metadata={
            'metadata': {
                'description': 'Number of packets received',
            }
        }
    )

    errors_in: int = field(
        metadata={
            'metadata': {
                'description': 'Number of errors on incoming traffic',
            },
        }
    )

    errors_out: int = field(
        metadata={
            'metadata': {
                'description': 'Number of errors on outgoing traffic',
            },
        }
    )

    drop_in: int = field(
        metadata={
            'metadata': {
                'description': 'Number of packets dropped on incoming traffic',
            },
        }
    )

    drop_out: int = field(
        metadata={
            'metadata': {
                'description': 'Number of packets dropped on outgoing traffic',
            },
        }
    )

    addresses: List['NetworkInterfaceAddress'] = field(
        default_factory=list,
        metadata={
            'metadata': {
                'description': 'List of addresses associated to the interface',
                'example': [
                    {
                        'family': AddressFamily.AF_INET.name,
                        'address': '192.168.1.2',
                        'netmask': '255.255.255.0',
                        'broadcast': '192.168.1.255',
                    }
                ],
            },
        },
    )


@dataclass
class NetworkInterfaceAddress:
    """
    Network interface address data class.
    """

    family: AddressFamily = field(
        metadata={
            'metadata': {
                'description': 'Address family',
                'example': AddressFamily.AF_INET.name,
            }
        }
    )

    address: Optional[str] = field(
        metadata={
            'metadata': {
                'description': 'IPv4 or IPv6 address of the interface',
                'example': '192.168.1.2',
            }
        }
    )

    netmask: Optional[str] = field(
        metadata={
            'metadata': {
                'description': 'Netmask for the interface address',
                'example': '255.255.255.0',
            }
        }
    )

    broadcast: Optional[str] = field(
        metadata={
            'metadata': {
                'description': 'Broadcast address for the interface',
                'example': '192.168.1.255',
            }
        }
    )
