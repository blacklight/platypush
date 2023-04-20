from marshmallow_dataclass import class_schema

from ._base import DiskBaseSchema
from ._model import Disk


DiskSchema = class_schema(Disk, base_schema=DiskBaseSchema)
