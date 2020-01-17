from typing import Optional, List, Union

from platypush.message import Mapping


class Pin(Mapping):
    """
    This class models the configuration for the PIN of a device.
    """
    def __init__(self, number: int, name: Optional[str] = None, pwm: bool = False, pull_up: bool = False):
        super().__init__(number=number, name=name, pwm=pwm, pull_up=pull_up)


class Device(Mapping):
    """
    This class models the properties of a configured ESP device.
    """
    def __init__(self, host: str, port: int = 8266, password: Optional[str] = None,
                 name: Optional[str] = None, pins: List[Union[Pin, dict]] = None):
        pins = [
            pin if isinstance(pin, Pin) else Pin(**pin)
            for pin in (pins or [])
        ]

        super().__init__(host=host, port=port, password=password, pins=pins, name=name)
        self._pin_by_name = {pin['name']: pin for pin in self['pins'] if pin['name']}
        self._pin_by_number = {pin['number']: pin for pin in self['pins']}

    def get_pin(self, pin) -> int:
        try:
            return int(pin)
        except ValueError:
            pass

        assert pin in self._pin_by_name, 'No such PIN configured: {}'.format(pin)
        return self._pin_by_name[pin]['number']


# vim:sw=4:ts=4:et:
