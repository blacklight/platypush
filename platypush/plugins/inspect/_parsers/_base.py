from abc import ABC, abstractmethod


class Parser(ABC):
    """
    Base class for parsers.
    """

    @classmethod
    @abstractmethod
    def parse(cls, docstring: str, obj_type: type) -> str:
        raise NotImplementedError()
