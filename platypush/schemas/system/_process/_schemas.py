from marshmallow_dataclass import class_schema

from ._base import ProcessBaseSchema
from ._model import Process


ProcessSchema = class_schema(Process, base_schema=ProcessBaseSchema)
