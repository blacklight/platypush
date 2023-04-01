from dataclasses import dataclass
from typing import Dict, List, Type
from typing_extensions import override

from platypush.common.sensors import Numeric
from platypush.entities.devices import Device
from platypush.entities.distance import DistanceSensor
from platypush.entities.humidity import HumiditySensor
from platypush.entities.pressure import PressureSensor
from platypush.entities.sensors import NumericSensor
from platypush.entities.temperature import TemperatureSensor
from platypush.plugins import action
from platypush.plugins.sensor import SensorPlugin


@dataclass
class SensorEntityMapping:
    """
    Maps the dict-like data returned by the plugin to corresponding sensor
    entities.
    """

    name: str
    unit: str
    entity_type: Type[NumericSensor]

    @property
    def id(self):
        """
        The standardized external ID for the entity.
        """
        return f'bme280:{self.name}'


_sensor_entity_mappings = {
    mapping.name: mapping
    for mapping in [
        SensorEntityMapping(
            name='temperature',
            unit='°C',
            entity_type=TemperatureSensor,
        ),
        SensorEntityMapping(
            name='humidity',
            unit='%',
            entity_type=HumiditySensor,
        ),
        SensorEntityMapping(
            name='pressure',
            unit='Pa',
            entity_type=PressureSensor,
        ),
        SensorEntityMapping(
            name='altitude',
            unit='m',
            entity_type=DistanceSensor,
        ),
    ]
}


# pylint: disable=too-many-ancestors
class SensorBme280Plugin(SensorPlugin):
    """
    Plugin to interact with a `BME280 <https://shop.pimoroni.com/products/bme280-breakout>`_ environment sensor for
    temperature, humidity and pressure measurements over I2C interface

    Requires:

        * ``pimoroni-bme280`` (``pip install pimoroni-bme280``)

    Triggers:

        * :class:`platypush.message.event.sensor.SensorDataAboveThresholdEvent`
        * :class:`platypush.message.event.sensor.SensorDataBelowThresholdEvent`
        * :class:`platypush.message.event.sensor.SensorDataChangeEvent`

    """

    def __init__(self, port: int = 1, **kwargs):
        """
        :param port: I2C port. 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)
        """

        super().__init__(**kwargs)
        self.port = port
        self._bus = None
        self._device = None

    def _get_device(self):
        from smbus import SMBus
        from bme280 import BME280

        if self._device:
            return self._device

        self._bus = SMBus(self.port)
        self._device = BME280(i2c_dev=self._bus)
        return self._device

    @override
    @action
    def get_measurement(self, *_, **__):
        """
        :returns: dict. Example:

        .. code-block:: python

           output = {
               "temperature": 21.0,   # Celsius
               "pressure": 101555.08, # Pascals
               "humidity": 23.543,    # percentage
               "altitude": 15.703     # meters
           }

        """

        device = self._get_device()
        return {
            'temperature': device.get_temperature(),
            'pressure': device.get_pressure() * 100,
            'humidity': device.get_humidity(),
            'altitude': device.get_altitude(),
        }

    @override
    def transform_entities(self, entities: Dict[str, Numeric]) -> List[Device]:
        sensors = []
        for sensor, value in entities.items():
            if value is None:
                continue

            mapping = _sensor_entity_mappings[sensor]
            sensors.append(
                mapping.entity_type(
                    id=mapping.id,
                    name=mapping.name,
                    value=value,
                    unit=mapping.unit,
                )
            )

        if not sensors:
            return []

        return [
            Device(
                id='bme280',
                name='BME280 Sensor',
                children=sensors,
            )
        ]


# vim:sw=4:ts=4:et:
