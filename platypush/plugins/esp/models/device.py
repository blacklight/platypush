from dataclasses import dataclass
from typing import Optional, List, Union


@dataclass
class Pin:
    """
    This class models the configuration for the PIN of a device.
    """

    number: int
    name: Optional[str] = None
    pwm: bool = False
    pull_up: bool = False


@dataclass
class Device:
    """
    This class models the properties of a configured ESP device.
    """

    host: str
    port: int = 8266
    password: Optional[str] = None
    name: Optional[str] = None
    pins: Optional[List[Union[Pin, dict]]] = None

    @property
    def _pins(self):
        return [
            pin if isinstance(pin, Pin) else Pin(**pin) for pin in (self.pins or [])
        ]

    @property
    def _pins_by_name(self):
        return {pin.name: pin for pin in self._pins if pin.name}

    @property
    def _pins_by_number(self):
        return {pin.number: pin for pin in self._pins}

    def get_pin(self, pin) -> int:
        try:
            return int(pin)
        except ValueError:
            pass

        pin_obj = self._pins_by_name.get(pin)
        assert pin_obj, f'No such PIN configured: {pin}'
        return pin_obj.number


# vim:sw=4:ts=4:et:
