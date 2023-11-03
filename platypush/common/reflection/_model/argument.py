from dataclasses import dataclass
from typing import Optional, Type

from .._serialize import Serializable
from .._utils import type_str


@dataclass
class Argument(Serializable):
    """
    Represents an integration constructor/action parameter.
    """

    name: str
    required: bool = False
    doc: Optional[str] = None
    type: Optional[Type] = None
    default: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "required": self.required,
            "doc": self.doc,
            "type": type_str(self.type),
            "default": self.default,
        }
