from dataclasses import dataclass
from typing import List, Optional

from ._battery import Battery
from ._cpu import Cpu
from ._disk import Disk
from ._fan import Fan
from ._memory import MemoryStats, SwapStats
from ._network import NetworkInterface
from ._temperature import Temperature


@dataclass
class SystemInfo:
    """
    Aggregate system info dataclass.
    """

    cpu: Cpu
    memory: MemoryStats
    swap: SwapStats
    disks: List[Disk]
    network: List[NetworkInterface]
    temperature: List[Temperature]
    fans: List[Fan]
    battery: Optional[Battery]
