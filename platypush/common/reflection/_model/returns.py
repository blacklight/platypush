from dataclasses import dataclass
from typing import Optional, Type

from .._serialize import Serializable
from .._utils import type_str


@dataclass
class ReturnValue(Serializable):
    """
    Represents the return value of an action.
    """

    doc: Optional[str] = None
    type: Optional[Type] = None

    def to_dict(self) -> dict:
        return {
            "doc": self.doc,
            "type": type_str(self.type),
        }
