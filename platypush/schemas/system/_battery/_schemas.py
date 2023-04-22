from marshmallow_dataclass import class_schema

from ._base import BatteryBaseSchema
from ._model import Battery


BatterySchema = class_schema(Battery, base_schema=BatteryBaseSchema)
