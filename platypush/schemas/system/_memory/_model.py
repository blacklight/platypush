from dataclasses import dataclass, field

from platypush.schemas.dataclasses import percent_field


@dataclass
class MemoryStats:
    """
    Memory stats data class.
    """

    total: int = field(
        metadata={
            'metadata': {
                'description': 'Total available memory, in bytes',
            }
        }
    )

    available: int = field(
        metadata={
            'metadata': {
                'description': 'Available memory, in bytes',
            }
        }
    )

    used: int = field(
        metadata={
            'metadata': {
                'description': 'Used memory, in bytes',
            }
        }
    )

    free: int = field(
        metadata={
            'metadata': {
                'description': 'Free memory, in bytes',
            }
        }
    )

    active: int = field(
        metadata={
            'metadata': {
                'description': 'Size of the active memory, in bytes',
            }
        }
    )

    inactive: int = field(
        metadata={
            'metadata': {
                'description': 'Size of the inactive memory, in bytes',
            }
        }
    )

    buffers: int = field(
        metadata={
            'metadata': {
                'description': 'Size of the buffered memory, in bytes',
            }
        }
    )

    cached: int = field(
        metadata={
            'metadata': {
                'description': 'Size of the cached memory, in bytes',
            }
        }
    )

    shared: int = field(
        metadata={
            'metadata': {
                'description': 'Size of the shared memory, in bytes',
            }
        }
    )

    percent: float = percent_field()


@dataclass
class SwapStats:
    """
    Swap memory stats data class.
    """

    total: int = field(
        metadata={
            'metadata': {
                'description': 'Total available memory, in bytes',
            }
        }
    )

    used: int = field(
        metadata={
            'metadata': {
                'description': 'Used memory, in bytes',
            }
        }
    )

    free: int = field(
        metadata={
            'metadata': {
                'description': 'Free memory, in bytes',
            }
        }
    )

    percent: float = percent_field()
