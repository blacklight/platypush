from typing import Union, Type, Callable

from .._parser import DocstringParser


class Constructor(DocstringParser):
    """
    Represents an integration constructor.
    """

    @classmethod
    def parse(cls, obj: Union[Type, Callable]) -> "Constructor":
        """
        Parse the parameters of a class constructor or action method.

        :param obj: Base type of the object.
        :return: The parsed parameters.
        """
        init = getattr(obj, "__init__", None)
        if init and callable(init):
            return super().parse(init)

        return super().parse(obj)
