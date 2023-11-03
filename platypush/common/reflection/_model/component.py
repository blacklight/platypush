from abc import ABC, abstractmethod
from typing import Dict, Type

from .argument import Argument


class Component(ABC):
    """
    Abstract interface for all the application components exposed through the
    `inspect` plugin.

    It includes integrations (plugins and backends) and messages (events and
    responses).
    """

    @staticmethod
    def _merge_params(params: Dict[str, Argument], new_params: Dict[str, Argument]):
        """
        Utility function to merge a new mapping of parameters into an existing one.
        """
        for param_name, param in new_params.items():
            # Set the parameter if it doesn't exist
            if param_name not in params:
                params[param_name] = param

            # Set the parameter documentation if it's not set
            if param.doc and not params[param_name].doc:
                params[param_name].doc = param.doc

            # If the new parameter has required=False,
            # then that should also be the value for the current ones
            if param.required is False:
                params[param_name].required = False

            # If the new parameter has a default value, and the current
            # one doesn't, then the default value should be set as the new one.
            if param.default is not None and params[param_name].default is None:
                params[param_name].default = param.default

    @classmethod
    @abstractmethod
    def by_name(cls, name: str) -> "Component":
        """
        :param name: Component type name.
        :return: A parsed component class given its name/type name.
        """

    @classmethod
    @abstractmethod
    def by_type(cls, type: Type) -> "Component":
        """
        :param type: Component type.
        :return: A parsed component class given its type.
        """

    @property
    @abstractmethod
    def cls(self) -> Type:
        """
        :return: The class of a component.
        """

    @property
    @abstractmethod
    def doc_url(self) -> str:
        """
        :return: The URL of the documentation of the component.
        """
