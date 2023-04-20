from dataclasses import dataclass, field
from typing import Optional


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
