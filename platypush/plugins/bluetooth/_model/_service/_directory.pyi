# mypy stub for ServiceClass

from enum import Enum

from platypush.plugins.bluetooth._types import RawServiceClass

class ServiceClass(Enum):
    """
    Enumeration of supported Bluetooth service classes.
    """

    value: RawServiceClass
    """ The raw service class value. """

    UNKNOWN = ...
    """ A class for unknown services. """
    OBEX_OBJECT_PUSH = ...
    """ Class for the OBEX Object Push service. """
    OBEX_FILE_TRANSFER = ...
    """ Class for the OBEX File Transfer service. """
    SWITCHBOT = ...
    """ Class for Switchbot devices services. """

    @classmethod
    def get(cls, value: RawServiceClass) -> "ServiceClass":
        """
        :param value: The raw service class UUID.
        :return: The parsed :class:`ServiceClass` instance, or
            ``ServiceClass.UNKNOWN``.
        """
    @classmethod
    def by_name(cls, name: str) -> "ServiceClass":
        """
        :param name: The name of the service class.
        :return: The :class:`ServiceClass` instance, or
            ``ServiceClass.UNKNOWN``.
        """
