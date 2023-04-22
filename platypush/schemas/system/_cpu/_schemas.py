from marshmallow_dataclass import class_schema

from .._base import SystemBaseSchema
from ._base import CpuInfoBaseSchema, CpuTimesBaseSchema
from ._model import CpuFrequency, CpuInfo, CpuStats, CpuTimes


CpuFrequencySchema = class_schema(CpuFrequency, base_schema=SystemBaseSchema)
CpuInfoSchema = class_schema(CpuInfo, base_schema=CpuInfoBaseSchema)
CpuTimesSchema = class_schema(CpuTimes, base_schema=CpuTimesBaseSchema)
CpuStatsSchema = class_schema(CpuStats, base_schema=SystemBaseSchema)
