from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from marshmallow import pre_load
from marshmallow.validate import Range
from marshmallow_dataclass import class_schema

from platypush.schemas.dataclasses import DataClassSchema


def percent_field(**kwargs):
    """
    Field used to model percentage float fields between 0 and 1.
    """
    return field(
        default_factory=float,
        metadata={
            'validate': Range(min=0, max=1),
            **kwargs,
        },
    )


class CpuInfoBaseSchema(DataClassSchema):
    """
    Base schema for CPU info.
    """

    @pre_load
    def pre_load(self, data: dict, **_) -> dict:
        if data.get('hz_advertised'):
            data['frequency_advertised'] = data.pop('hz_advertised')[0]
        if data.get('hz_actual'):
            data['frequency_actual'] = data.pop('hz_actual')[0]

        return data


class MemoryStatsBaseSchema(DataClassSchema):
    """
    Base schema for memory stats.
    """

    @pre_load
    def pre_load(self, data: dict, **_) -> dict:
        # Normalize the percentage between 0 and 1
        if data.get('percent') is not None:
            data['percent'] /= 100
        return data


class CpuTimesBaseSchema(DataClassSchema):
    """
    Base schema for CPU times.
    """

    @pre_load
    def pre_load(self, data, **_) -> dict:
        """
        Convert the underlying object to dict and normalize all the percentage
        values from [0, 100] to [0, 1].
        """
        return {
            key: value / 100.0
            for key, value in (
                data if isinstance(data, dict) else data._asdict()
            ).items()
        }


class DiskBaseSchema(DataClassSchema):
    """
    Base schema for disk stats.
    """

    @pre_load
    def pre_load(self, data: dict, **_) -> dict:
        # Convert read/write/busy times from milliseconds to seconds
        for attr in ['read_time', 'write_time', 'busy_time']:
            if data.get(attr) is not None:
                data[attr] /= 1000

        # Normalize the percentage between 0 and 1
        if data.get('percent') is not None:
            data['percent'] /= 100

        return data


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
class CpuData:
    """
    CPU data aggregate dataclass.
    """

    info: CpuInfo
    times: CpuTimes
    frequency: CpuFrequency
    stats: CpuStats
    load_avg: Tuple[float, float, float]
    percent: float = percent_field()


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

    read_count: int = field(
        metadata={
            'metadata': {
                'description': 'Number of recorded read operations',
            }
        }
    )

    write_count: int = field(
        metadata={
            'metadata': {
                'description': 'Number of recorded write operations',
            }
        }
    )

    read_bytes: int = field(
        metadata={
            'metadata': {
                'description': 'Number of read bytes',
            }
        }
    )

    write_bytes: int = field(
        metadata={
            'metadata': {
                'description': 'Number of written bytes',
            }
        }
    )

    read_time: float = field(
        metadata={
            'metadata': {
                'description': 'Time spent reading, in seconds',
            }
        }
    )

    write_time: float = field(
        metadata={
            'metadata': {
                'description': 'Time spent writing, in seconds',
            }
        }
    )

    busy_time: float = field(
        metadata={
            'metadata': {
                'description': 'Total disk busy time, in seconds',
            }
        }
    )

    percent: float = percent_field()


@dataclass
class SystemInfo:
    """
    Aggregate system info dataclass.
    """

    cpu: CpuData
    memory: MemoryStats
    swap: SwapStats
    disks: List[Disk]


CpuFrequencySchema = class_schema(CpuFrequency, base_schema=DataClassSchema)
CpuInfoSchema = class_schema(CpuInfo, base_schema=CpuInfoBaseSchema)
CpuTimesSchema = class_schema(CpuTimes, base_schema=CpuTimesBaseSchema)
CpuStatsSchema = class_schema(CpuStats, base_schema=DataClassSchema)
DiskSchema = class_schema(Disk, base_schema=DiskBaseSchema)
MemoryStatsSchema = class_schema(MemoryStats, base_schema=MemoryStatsBaseSchema)
SwapStatsSchema = class_schema(SwapStats, base_schema=MemoryStatsBaseSchema)
SystemInfoSchema = class_schema(SystemInfo, base_schema=DataClassSchema)
