from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from platypush.schemas.dataclasses import percent_field


@dataclass
class CpuInfo:
    """
    CPU info data class.
    """

    architecture: Optional[str] = field(
        metadata={
            'data_key': 'arch_string_raw',
            'metadata': {
                'description': 'CPU architecture',
                'example': 'x86_64',
            },
        }
    )

    bits: int = field(
        metadata={
            'metadata': {
                'description': 'CPU bits / register size',
                'example': 64,
            }
        }
    )

    cores: int = field(
        metadata={
            'data_key': 'count',
            'metadata': {
                'description': 'Number of cores',
                'example': 4,
            },
        }
    )

    vendor: Optional[str] = field(
        metadata={
            'data_key': 'vendor_id_raw',
            'metadata': {
                'description': 'Vendor string',
                'example': 'GenuineIntel',
            },
        }
    )

    brand: Optional[str] = field(
        metadata={
            'data_key': 'brand_raw',
            'metadata': {
                'description': 'CPU brand string',
                'example': 'Intel(R) Core(TM) i7-5500U CPU @ 2.40GHz',
            },
        }
    )

    frequency_advertised: Optional[int] = field(
        metadata={
            'metadata': {
                'description': 'Advertised CPU frequency, in Hz',
                'example': 2400000000,
            }
        }
    )

    frequency_actual: Optional[int] = field(
        metadata={
            'metadata': {
                'description': 'Actual CPU frequency, in Hz',
                'example': 2350000000,
            }
        }
    )

    flags: List[str] = field(
        metadata={
            'metadata': {
                'description': 'CPU flags',
                'example': ['acpi', 'aes', 'cpuid'],
            }
        }
    )

    l1_instruction_cache_size: Optional[int] = field(
        metadata={
            'metadata': {
                'description': 'Size of the L1 instruction cache, in bytes',
                'example': 65536,
            }
        }
    )

    l1_data_cache_size: Optional[int] = field(
        metadata={
            'metadata': {
                'description': 'Size of the L1 data cache, in bytes',
                'example': 65536,
            }
        }
    )

    l2_cache_size: Optional[int] = field(
        metadata={
            'metadata': {
                'description': 'Size of the L2 cache, in bytes',
                'example': 524288,
            }
        }
    )

    l3_cache_size: Optional[int] = field(
        metadata={
            'metadata': {
                'description': 'Size of the L2 cache, in bytes',
                'example': 4194304,
            }
        }
    )


@dataclass
class CpuTimes:
    """
    CPU times data class.
    """

    user: Optional[float] = percent_field()
    nice: Optional[float] = percent_field()
    system: Optional[float] = percent_field()
    idle: Optional[float] = percent_field()
    iowait: Optional[float] = percent_field()
    irq: Optional[float] = percent_field()
    softirq: Optional[float] = percent_field()
    steal: Optional[float] = percent_field()
    guest: Optional[float] = percent_field()
    guest_nice: Optional[float] = percent_field()


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
    percent: float = percent_field()
