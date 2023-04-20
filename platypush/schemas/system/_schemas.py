from marshmallow_dataclass import class_schema

from platypush.schemas.dataclasses import DataClassSchema

from ._model import SystemInfo


SystemInfoSchema = class_schema(SystemInfo, base_schema=DataClassSchema)
