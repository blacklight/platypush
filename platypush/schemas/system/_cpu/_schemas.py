from marshmallow_dataclass import class_schema

from platypush.schemas.dataclasses import DataClassSchema

from ._base import CpuInfoBaseSchema, CpuTimesBaseSchema
from ._model import CpuFrequency, CpuInfo, CpuStats, CpuTimes


CpuFrequencySchema = class_schema(CpuFrequency, base_schema=DataClassSchema)
CpuInfoSchema = class_schema(CpuInfo, base_schema=CpuInfoBaseSchema)
CpuTimesSchema = class_schema(CpuTimes, base_schema=CpuTimesBaseSchema)
CpuStatsSchema = class_schema(CpuStats, base_schema=DataClassSchema)
