from marshmallow_dataclass import class_schema

from ._base import UserBaseSchema
from ._model import User


UserSchema = class_schema(User, base_schema=UserBaseSchema)
