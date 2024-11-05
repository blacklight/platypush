from marshmallow import fields, pre_load

from platypush.schemas.dataclasses import percent_field
from .._base import SystemBaseSchema


class CpuInfoSchema(SystemBaseSchema):
    """
    Base schema for CPU info.
    """

    architecture = fields.String(
        data_key='arch_string_raw',
        metadata={
            'description': 'CPU architecture.',
            'example': 'x86_64',
        },
    )

    bits = fields.Int(
        metadata={
            'description': 'CPU architecture bits.',
            'example': 64,
        }
    )

    cores = fields.Int(
        data_key='count',
        metadata={
            'description': 'Number of CPU cores.',
            'example': 4,
        },
    )

    vendor = fields.String(
        data_key='vendor_id_raw',
        metadata={
            'description': 'CPU vendor.',
            'example': 'GenuineIntel',
        },
    )

    brand = fields.String(
        data_key='brand_raw',
        metadata={
            'description': 'CPU brand.',
            'example': 'Intel(R) Core(TM) i7-7700HQ CPU @ 2.80GHz',
        },
    )

    frequency_advertised = fields.Float(
        metadata={
            'description': 'CPU advertised frequency.',
            'example': 2800000000.0,
        }
    )

    frequency_actual = fields.Float(
        metadata={
            'description': 'CPU actual frequency.',
            'example': 2650000000.0,
        }
    )

    flags = fields.List(
        fields.String(),
        metadata={
            'description': 'CPU flags.',
            'example': ['fpu', 'vme', 'de', 'pse', 'tsc', 'msr', 'pae'],
        },
    )

    l1_instruction_cache_size = fields.Int(
        metadata={
            'description': 'L1 instruction cache size.',
            'example': 65536,
        }
    )

    l1_data_cache_size = fields.Int(
        metadata={
            'description': 'L1 data cache size.',
            'example': 65536,
        }
    )

    l2_cache_size = fields.Int(
        metadata={
            'description': 'L2 cache size.',
            'example': 524288,
        }
    )

    l3_cache_size = fields.Int(
        metadata={
            'description': 'L3 cache size.',
            'example': 6291456,
        }
    )

    @pre_load
    def pre_load(self, data: dict, **_) -> dict:
        data = super().pre_load(data)
        if data.get('hz_advertised'):
            data['frequency_advertised'] = data.pop('hz_advertised')[0]
        if data.get('hz_actual'):
            data['frequency_actual'] = data.pop('hz_actual')[0]

        for key, value in data.items():
            if key.endswith("_cache_size") and isinstance(value, str):
                tokens = value.split(" ")
                unit = None
                if len(tokens) > 1:
                    unit = tokens[1]

                value = int(tokens[0])
                if unit == "KiB":
                    value *= 1024
                elif unit == "MiB":
                    value *= 1024 * 1024
                elif unit == "GiB":
                    value *= 1024 * 1024 * 1024

                data[key] = value

        return data


class CpuTimesSchema(SystemBaseSchema):
    """
    Base schema for CPU times.
    """

    user = percent_field(
        metadata={
            'description': 'Time spent in user mode, '
            'as a percentage between 0 and 1 of the total CPU time.',
            'example': 0.0,
        }
    )

    nice = percent_field(
        metadata={
            'description': 'Time spent in nice mode, '
            'as a percentage between 0 and 1 of the total CPU time.',
            'example': 0.0,
        }
    )

    system = percent_field(
        metadata={
            'description': 'Time spent in system mode, '
            'as a percentage between 0 and 1 of the total CPU time.',
            'example': 0.0,
        }
    )

    idle = percent_field(
        metadata={
            'description': 'Time spent in idle mode, '
            'as a percentage between 0 and 1 of the total CPU time.',
            'example': 0.0,
        }
    )

    iowait = percent_field(
        metadata={
            'description': 'Time spent in I/O wait mode, '
            'as a percentage between 0 and 1 of the total CPU time.',
            'example': 0.0,
        }
    )

    irq = percent_field(
        metadata={
            'description': 'Time spent in IRQ mode, '
            'as a percentage between 0 and 1 of the total CPU time.',
            'example': 0.0,
        }
    )

    softirq = percent_field(
        metadata={
            'description': 'Time spent in soft IRQ mode, '
            'as a percentage between 0 and 1 of the total CPU time.',
            'example': 0.0,
        }
    )

    steal = percent_field(
        metadata={
            'description': 'Time spent in steal mode, '
            'as a percentage between 0 and 1 of the total CPU time.',
            'example': 0.0,
        }
    )

    guest = percent_field(
        metadata={
            'description': 'Time spent in guest mode, '
            'as a percentage between 0 and 1 of the total CPU time.',
            'example': 0.0,
        }
    )

    guest_nice = percent_field(
        metadata={
            'description': 'Time spent in guest nice mode, '
            'as a percentage between 0 and 1 of the total CPU time.',
            'example': 0.0,
        }
    )

    @pre_load
    def pre_load(self, data, **_) -> dict:
        """
        Convert the underlying object to dict and normalize all the percentage
        values from [0, 100] to [0, 1].
        """
        data = super().pre_load(data)
        return {
            key: value / 100.0
            for key, value in (
                data if isinstance(data, dict) else data._asdict()
            ).items()
        }


class CpuFrequencySchema(SystemBaseSchema):
    """
    Base schema for CPU frequency.
    """

    current = fields.Float(
        metadata={
            'description': 'Current CPU frequency.',
            'example': 2800000000.0,
        }
    )

    min = fields.Float(
        metadata={
            'description': 'Minimum CPU frequency.',
            'example': 800000000.0,
        }
    )

    max = fields.Float(
        metadata={
            'description': 'Maximum CPU frequency.',
            'example': 2800000000.0,
        }
    )


class CpuStatsSchema(SystemBaseSchema):
    """
    Base schema for CPU stats.
    """

    ctx_switches = fields.Int(
        metadata={
            'description': 'Number of context switches.',
            'example': 1234,
        }
    )

    interrupts = fields.Int(
        metadata={
            'description': 'Number of interrupts.',
            'example': 1234,
        }
    )

    soft_interrupts = fields.Int(
        metadata={
            'description': 'Number of soft interrupts.',
            'example': 1234,
        }
    )

    syscalls = fields.Int(
        metadata={
            'description': 'Number of system calls.',
            'example': 1234,
        }
    )


class CpuSchema(SystemBaseSchema):
    """
    Base schema for CPU results.
    """

    info = fields.Nested(CpuInfoSchema)
    times = fields.Nested(CpuTimesSchema)
    frequency = fields.Nested(CpuFrequencySchema)
    stats = fields.Nested(CpuStatsSchema)
    load_avg = fields.Tuple(
        [fields.Float(), fields.Float(), fields.Float()],
        metadata={
            'description': 'CPU load average.',
            'example': (0.0, 0.0, 0.0),
        },
    )

    percent = percent_field(
        metadata={
            'description': 'CPU usage percentage, as a value between 0 and 1.',
            'example': 0.0,
        }
    )
