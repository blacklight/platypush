import contextlib
import importlib
import inspect
from dataclasses import dataclass
from typing import Type, Optional

from .._serialize import Serializable
from . import Constructor
from .component import Component
from .constants import doc_base_url


@dataclass
class Message(Component, Serializable):
    """
    Represents the metadata of a message type (event or response).
    """

    name: str
    type: Type
    doc: Optional[str] = None
    constructor: Optional[Constructor] = None

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "type": f"{self.type.__module__}.{self.type.__qualname__}",
            "doc": self.doc,
            "doc_url": self.doc_url,
            "args": {
                **(
                    {name: arg.to_dict() for name, arg in self.constructor.args.items()}
                    if self.constructor
                    else {}
                ),
            },
        }

    @classmethod
    def by_name(cls, name: str) -> "Message":
        """
        :param name: Message type name.
        :return: A parsed message class given its type.
        """
        return cls.by_type(cls._get_cls(name))

    @classmethod
    def by_type(cls, type: Type) -> "Message":
        """
        :param type: Message type.
        :return: A parsed message class given its type.
        """
        from platypush.message import Message as MessageClass

        assert issubclass(type, MessageClass), f"Expected a Message class, got {type}"
        obj = cls(
            name=f'{type.__module__}.{type.__qualname__}',
            type=type,
            doc=inspect.getdoc(type),
            constructor=Constructor.parse(type),
        )

        for p_type in inspect.getmro(type)[1:]:
            # Don't go upper in the hierarchy.
            if p_type == type:
                break

            with contextlib.suppress(AssertionError):
                p_obj = cls.by_type(p_type)
                # Merge constructor parameters
                if obj.constructor and p_obj.constructor:
                    cls._merge_params(obj.constructor.args, p_obj.constructor.args)

        return obj

    @property
    def cls(self) -> Type:
        """
        :return: The class of a message.
        """
        return self._get_cls(self.name)

    @staticmethod
    def _get_cls(name: str) -> Type:
        """
        :param name: Full qualified type name, module included.
        :return: The associated class.
        """
        tokens = name.split(".")
        module = importlib.import_module(".".join(tokens[:-1]))
        return getattr(module, tokens[-1])

    @property
    def doc_url(self) -> str:
        """
        :return: URL of the documentation for the message.
        """
        from platypush.message.event import Event
        from platypush.message.response import Response

        if issubclass(self.type, Event):
            section = 'events'
        elif issubclass(self.type, Response):
            section = 'responses'
        else:
            raise AssertionError(f'Unknown message type {self.type}')

        mod_name = '.'.join(self.name.split('.')[3:-1])
        return f"{doc_base_url}/{section}/{mod_name}.html#{self.name}"
