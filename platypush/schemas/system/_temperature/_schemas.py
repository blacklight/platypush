from marshmallow_dataclass import class_schema

from ._base import TemperatureBaseSchema
from ._model import Temperature


TemperatureSchema = class_schema(Temperature, base_schema=TemperatureBaseSchema)
