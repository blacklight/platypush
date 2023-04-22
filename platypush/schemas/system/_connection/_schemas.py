from marshmallow_dataclass import class_schema

from ._base import ConnectionBaseSchema
from ._model import Connection


ConnectionSchema = class_schema(Connection, base_schema=ConnectionBaseSchema)
