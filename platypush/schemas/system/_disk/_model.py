from dataclasses import dataclass
from typing import Optional


@dataclass
class Disk:
    """
    Disk data class.
    """

    device: str
    mountpoint: Optional[str] = None
    fstype: Optional[str] = None
    opts: Optional[str] = None
    total: Optional[int] = None
    used: Optional[int] = None
    free: Optional[int] = None
    read_count: Optional[int] = None
    write_count: Optional[int] = None
    read_bytes: Optional[int] = None
    write_bytes: Optional[int] = None
    read_time: Optional[float] = None
    write_time: Optional[float] = None
    busy_time: Optional[float] = None
    percent: Optional[float] = None
