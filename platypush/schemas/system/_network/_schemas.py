from marshmallow_dataclass import class_schema

from ._base import NetworkInterfaceBaseSchema
from ._model import NetworkInterface


NetworkInterfaceSchema = class_schema(
    NetworkInterface, base_schema=NetworkInterfaceBaseSchema
)
