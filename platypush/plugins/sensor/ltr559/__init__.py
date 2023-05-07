from typing import Dict, List

from typing_extensions import override

from platypush.common.sensors import Numeric
from platypush.entities.devices import Device
from platypush.entities.distance import DistanceSensor
from platypush.entities.illuminance import IlluminanceSensor
from platypush.plugins import action
from platypush.plugins.sensor import SensorPlugin


# pylint: disable=too-many-ancestors
class SensorLtr559Plugin(SensorPlugin):
    """
    Plugin to interact with an `LTR559 <https://shop.pimoroni.com/products/ltr-559-light-proximity-sensor-breakout>`_
    light and proximity sensor

    Requires:

        * ``ltr559`` (``pip install ltr559``)
        * ``smbus`` (``pip install smbus``)

    Triggers:

        * :class:`platypush.message.event.sensor.SensorDataAboveThresholdEvent`
        * :class:`platypush.message.event.sensor.SensorDataBelowThresholdEvent`
        * :class:`platypush.message.event.sensor.SensorDataChangeEvent`

    """

    def __init__(self, **kwargs):
        import ltr559

        super().__init__(**kwargs)
        self.ltr = ltr559.LTR559()

    @override
    @action
    def get_measurement(self, *_, **__):
        """
        :returns: dict. Example:

          .. code-block:: python

             output = {
                 "light": 109.3543,     # Lux
                 "proximity": 103       # The higher the value, the nearest the object, within a ~5cm range
             }

        """
        self.ltr.update_sensor()
        return {
            'light': self.ltr.get_lux(),
            'proximity': self.ltr.get_proximity(),
        }

    @override
    def transform_entities(self, entities: Dict[str, Numeric]) -> List[Device]:
        sensors = []

        if entities.get('light') is not None:
            sensors.append(
                IlluminanceSensor(
                    id='ltr559:illuminance',
                    name='illuminance',
                    value=entities['light'],
                    unit='lux',
                )
            )

        if entities.get('proximity') is not None:
            sensors.append(
                DistanceSensor(
                    id='ltr559:proximity',
                    name='proximity',
                    value=entities['proximity'],
                    unit='mm',
                )
            )

        if not sensors:
            return []

        return [
            Device(
                id='ltr559',
                name='LTR559 Sensor',
                children=sensors,
            )
        ]


# vim:sw=4:ts=4:et:
