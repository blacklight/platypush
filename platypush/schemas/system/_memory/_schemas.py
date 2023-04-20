from marshmallow_dataclass import class_schema

from ._base import MemoryStatsBaseSchema
from ._model import MemoryStats, SwapStats


MemoryStatsSchema = class_schema(MemoryStats, base_schema=MemoryStatsBaseSchema)
SwapStatsSchema = class_schema(SwapStats, base_schema=MemoryStatsBaseSchema)
