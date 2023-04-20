from dataclasses import dataclass
from typing import List

from ._cpu import Cpu
from ._disk import Disk
from ._memory import MemoryStats, SwapStats
from ._network import NetworkInterface


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
