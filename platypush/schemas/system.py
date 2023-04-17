from dataclasses import dataclass, field
from typing import List, Optional

from marshmallow import pre_load
from marshmallow.validate import Range
from marshmallow_dataclass import class_schema

from platypush.schemas.dataclasses import DataClassSchema


def percent_field(**kwargs):
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
class CpuData:
    """
    CPU data aggregate dataclass.
    """

    info: CpuInfo
    times: CpuTimes
    percent: float = percent_field()


@dataclass
class SystemInfo:
    """
    Aggregate system info dataclass.
    """

    cpu: CpuData


CpuInfoSchema = class_schema(CpuInfo, base_schema=CpuInfoBaseSchema)
CpuTimesSchema = class_schema(CpuTimes, base_schema=CpuTimesBaseSchema)
CpuDataSchema = class_schema(CpuTimes, base_schema=DataClassSchema)
SystemInfoSchema = class_schema(SystemInfo, base_schema=DataClassSchema)
