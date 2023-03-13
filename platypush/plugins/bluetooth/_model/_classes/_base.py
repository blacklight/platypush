from enum import Enum
from dataclasses import dataclass
from typing import Optional


class BaseBluetoothClass(Enum):
    """
    Base enum to model Bluetooth device/service classes.
    """

    def __repr__(self) -> str:
        """
        :return: The enum class formatted as ``<name: <value>``.
        """
        return f'<{self.__class__.__name__}.{self.name}: {str(self)}>'

    def __str__(self) -> str:
        """
        :return Only the readable string value of the class.
        """
        return self.value.name


@dataclass
class ClassProperty:
    """
    Models a Bluetooth class property.

    Given a Bluetooth class as a 24-bit unsigned integer, this class models the
    filter that should be applied to the class to tell if the device exposes the
    property.
    """

    name: str
    """ The name of the property. """
    bitmask: int
    """ Bitmask used to select the property bits from the class. """
    bit_shift: int = 0
    """ Number of bits to shift the class value after applying the bitmask. """
    match_value: int = 1
    """
    This should be the result of the bitwise filter for the property to match.
    """
    parent: Optional[BaseBluetoothClass] = None
    """
    Parent class property, if this is a minor property. If this is the case,
    then the advertised class value should also match the parent property.
    """

    def matches(self, cls: int) -> bool:
        """
        Match function.

        :param cls: The Bluetooth composite class value.
        :return: True if the class matches the property.
        """
        if self.parent and not self.parent.value.matches(cls):
            return False
        return ((cls & self.bitmask) >> self.bit_shift) == self.match_value
