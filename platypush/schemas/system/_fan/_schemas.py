from marshmallow_dataclass import class_schema

from ._base import FanBaseSchema
from ._model import Fan


FanSchema = class_schema(Fan, base_schema=FanBaseSchema)
