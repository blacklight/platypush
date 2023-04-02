from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Type
from typing_extensions import override

from platypush.common.sensors import Numeric
from platypush.entities.acceleration import Accelerometer
from platypush.entities.devices import Device
from platypush.entities.distance import DistanceSensor
from platypush.entities.illuminance import IlluminanceSensor
from platypush.entities.magnetism import Magnetometer
from platypush.entities.pressure import PressureSensor
from platypush.entities.sensors import BinarySensor, RawSensor, Sensor
from platypush.entities.temperature import TemperatureSensor
from platypush.plugins import action
from platypush.plugins.sensor import SensorPlugin


@dataclass
class SensorEntityMapping:
    """
    Maps sensor attributes returned by
    :meth:`SensorEnvirophatPlugin.get_measurement` to native sensor entities.
    """

    name: str
    entity_type: Type[Sensor]
    unit: Optional[str] = None
    kwargs: Dict[str, Any] = field(default_factory=dict)

    @property
    def id(self):
        """
        Standard format for an Envirophat sensor external ID.
        """
        return f'envirophat:{self.name}'


_sensor_entity_mappings: Dict[str, SensorEntityMapping] = {
    mapping.name: mapping
    for mapping in [
        SensorEntityMapping(
            name='temperature',
            entity_type=TemperatureSensor,
            unit='°C',
        ),
        SensorEntityMapping(
            name='pressure',
            entity_type=PressureSensor,
            unit='Pa',
        ),
        SensorEntityMapping(
            name='altitude',
            entity_type=DistanceSensor,
            unit='m',
        ),
        SensorEntityMapping(
            name='illuminance',
            entity_type=IlluminanceSensor,
            unit='lux',
        ),
        SensorEntityMapping(
            name='accelerometer',
            entity_type=Accelerometer,
        ),
        SensorEntityMapping(
            name='magnetometer',
            entity_type=Magnetometer,
        ),
        SensorEntityMapping(
            name='analog',
            entity_type=RawSensor,
        ),
        SensorEntityMapping(
            name='leds',
            entity_type=BinarySensor,
        ),
    ]
}


# pylint: disable=too-many-ancestors
class SensorEnvirophatPlugin(SensorPlugin):
    """
    Plugin to interact with a `Pimoroni enviropHAT
    <https://shop.pimoroni.com/products/enviro-phat>`_ device.

    You can use an enviropHAT device to read e.g. temperature, pressure,
    altitude, accelerometer, magnetometer and luminosity data.

    Requires:

        * ``envirophat`` (``pip install envirophat``)

    Triggers:

        * :class:`platypush.message.event.sensor.SensorDataAboveThresholdEvent`
        * :class:`platypush.message.event.sensor.SensorDataBelowThresholdEvent`
        * :class:`platypush.message.event.sensor.SensorDataChangeEvent`

    """

    @override
    @action
    def get_measurement(self, *_, qnh: float = 1020.0, **__):
        """
        :param: qnh: Local value for atmospheric pressure adjusted to sea level
            (default: 1020)

        :returns: dict. Example:

        .. code-block:: python

           output = {
               "temperature": 21.0,   # Celsius
               "pressure": 101555.08, # pascals
               "altitude": 10,        # meters
               "luminosity": 426,     # lumens

               # Measurements from the custom analog channels
               "analog": [0.513, 0.519, 0.531, 0.528],

               "accelerometer": {
                   "x": -0.000915,
                   "y": 0.0760,
                   "z": 1.026733
               },
               "magnetometer": {
                   "x": -2297,
                   "y": 1226,
                   "z": -7023
               },
           }

        """

        import envirophat

        ret = {}
        weather = envirophat.weather
        light = envirophat.light
        accelerometer = envirophat.motion.accelerometer()
        magnetometer = envirophat.motion.magnetometer()
        leds = envirophat.leds
        analog = envirophat.analog

        weather.update()

        ret['temperature'] = weather.temperature()
        ret['pressure'] = weather.pressure()
        ret['altitude'] = weather.altitude(qnh=qnh)
        ret['luminosity'] = light.light()
        ret['accelerometer'] = {v: getattr(accelerometer, v) for v in ['x', 'y', 'z']}
        ret['magnetometer'] = {v: getattr(magnetometer, v) for v in ['x', 'y', 'z']}
        ret['analog'] = list(analog.read_all())
        ret['leds'] = leds.is_on()

        return ret

    @override
    def transform_entities(self, entities: Dict[str, Numeric]) -> List[Device]:
        return [
            Device(
                id='envirophat',
                name='EnviroPHAT',
                children=[
                    _sensor_entity_mappings[sensor].entity_type(
                        id=_sensor_entity_mappings[sensor].id,
                        name=_sensor_entity_mappings[sensor].name,
                        unit=_sensor_entity_mappings[sensor].unit,
                        **_sensor_entity_mappings[sensor].kwargs,
                    )
                    for sensor, value in entities.items()
                    if value is not None
                ],
            )
        ]


# vim:sw=4:ts=4:et:
