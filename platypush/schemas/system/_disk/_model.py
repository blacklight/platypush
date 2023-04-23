from dataclasses import dataclass, field
from typing import Optional

from platypush.schemas.dataclasses import percent_field


@dataclass
class Disk:
    """
    Disk data class.
    """

    device: str = field(
        metadata={
            'metadata': {
                'description': 'Path/identifier of the disk/partition',
                'example': '/dev/sda1',
            }
        }
    )

    mountpoint: Optional[str] = field(
        metadata={
            'metadata': {
                'description': 'Where the disk is mounted',
                'example': '/home',
            }
        }
    )

    fstype: Optional[str] = field(
        metadata={
            'metadata': {
                'description': 'Filesystem type',
                'example': 'ext4',
            }
        }
    )

    opts: Optional[str] = field(
        metadata={
            'metadata': {
                'description': 'Extra mount options passed to the partition',
                'example': 'rw,relatime,fmask=0022,dmask=0022,utf8',
            }
        }
    )

    total: int = field(
        metadata={
            'metadata': {
                'description': 'Total available space, in bytes',
            }
        }
    )

    used: int = field(
        metadata={
            'metadata': {
                'description': 'Used disk space, in bytes',
            }
        }
    )

    free: int = field(
        metadata={
            'metadata': {
                'description': 'Free disk space, in bytes',
            }
        }
    )

    read_count: Optional[int] = field(
        metadata={
            'metadata': {
                'description': 'Number of recorded read operations',
            }
        }
    )

    write_count: Optional[int] = field(
        metadata={
            'metadata': {
                'description': 'Number of recorded write operations',
            }
        }
    )

    read_bytes: Optional[int] = field(
        metadata={
            'metadata': {
                'description': 'Number of read bytes',
            }
        }
    )

    write_bytes: Optional[int] = field(
        metadata={
            'metadata': {
                'description': 'Number of written bytes',
            }
        }
    )

    read_time: Optional[float] = field(
        metadata={
            'metadata': {
                'description': 'Time spent reading, in seconds',
            }
        }
    )

    write_time: Optional[float] = field(
        metadata={
            'metadata': {
                'description': 'Time spent writing, in seconds',
            }
        }
    )

    busy_time: Optional[float] = field(
        metadata={
            'metadata': {
                'description': 'Total disk busy time, in seconds',
            }
        }
    )

    percent: float = percent_field()
