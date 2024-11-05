from dataclasses import dataclass, field
from typing import List, Optional, Tuple


@dataclass
class CpuInfo:
    """
    CPU info data class.
    """

    bits: int
    cores: int
    architecture: Optional[str] = None
    vendor: Optional[str] = None
    brand: Optional[str] = None
    frequency_advertised: Optional[float] = None
    frequency_actual: Optional[float] = None
    flags: List[str] = field(default_factory=list)
    l1_instruction_cache_size: Optional[float] = None
    l1_data_cache_size: Optional[float] = None
    l2_cache_size: Optional[float] = None
    l3_cache_size: Optional[float] = None


@dataclass
class CpuTimes:
    """
    CPU times data class.
    """

    user: Optional[float] = None
    nice: Optional[float] = None
    system: Optional[float] = None
    idle: Optional[float] = None
    iowait: Optional[float] = None
    irq: Optional[float] = None
    softirq: Optional[float] = None
    steal: Optional[float] = None
    guest: Optional[float] = None
    guest_nice: Optional[float] = None


@dataclass
class CpuStats:
    """
    CPU stats data class.
    """

    ctx_switches: int
    interrupts: int
    soft_interrupts: int
    syscalls: int


@dataclass
class CpuFrequency:
    """
    CPU frequency data class.
    """

    current: float
    min: float
    max: float


@dataclass
class Cpu:
    """
    CPU data aggregate dataclass.
    """

    info: CpuInfo
    times: CpuTimes
    frequency: CpuFrequency
    stats: CpuStats
    load_avg: Tuple[float, float, float]
    percent: float
