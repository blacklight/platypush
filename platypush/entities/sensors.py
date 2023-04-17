import json
import logging
from typing import Optional, Union

from sqlalchemy import (
    Boolean,
    Column,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
)

from platypush.common.db import Base

from .devices import Device

logger = logging.getLogger(__name__)


class Sensor(Device):
    """
    Abstract class for sensor entities. A sensor entity is, by definition, an
    entity with the ``is_read_only`` property set to ``True``.
    """

    __abstract__ = True

    def __init__(self, *args, **kwargs):
        kwargs['is_read_only'] = True
        super().__init__(*args, **kwargs)


if 'raw_sensor' not in Base.metadata:

    class RawSensor(Sensor):
        """
        Models a raw sensor, whose value can contain either a string, a
        hex-encoded binary string, or a JSON-encoded object.
        """

        __tablename__ = 'raw_sensor'

        id = Column(
            Integer, ForeignKey(Device.id, ondelete='CASCADE'), primary_key=True
        )
        _value = Column(String)
        is_binary = Column(Boolean, default=False)
        """ If ``is_binary`` is ``True``, then ``value`` is a hex string. """
        is_json = Column(Boolean, default=False)
        """
        If ``is_json`` is ``True``, then ``value`` is a JSON-encoded string
        object or array.
        """
        unit = Column(String)

        @property
        def value(self):
            if self._value is None:
                return None
            if self.is_binary and isinstance(self._value, str):
                value = self._value[2:]
                return bytes(
                    [int(value[i : i + 2], 16) for i in range(0, len(value), 2)]
                )
            if self.is_json and isinstance(self._value, (str, bytes)):
                return json.loads(self._value)
            return self._value

        @value.setter
        def value(
            self, value: Optional[Union[str, bytearray, bytes, list, tuple, set, dict]]
        ):
            if isinstance(value, (bytearray, bytes)):
                self._value = '0x' + ''.join([f'{x:02x}' for x in value])
                self.is_binary = True
            elif isinstance(value, (list, tuple, set)):
                self._value = json.dumps(list(value))
                self.is_json = True
            elif isinstance(value, dict):
                self._value = json.dumps(value)
                self.is_json = True
            else:
                self._value = value
                self.is_binary = False
                self.is_json = False

        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }


if 'numeric_sensor' not in Base.metadata and 'percent_sensor' not in Base.metadata:

    class NumericSensor(Sensor):
        """
        Models a numeric sensor, with a numeric value and an optional min/max
        range.
        """

        __tablename__ = 'numeric_sensor'

        id = Column(
            Integer, ForeignKey(Device.id, ondelete='CASCADE'), primary_key=True
        )
        value = Column(Float)
        min = Column(Float)
        max = Column(Float)
        unit = Column(String)

        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }

    class PercentSensor(NumericSensor):
        """
        A subclass of ``NumericSensor`` that represents a percentage value.
        """

        __tablename__ = 'percent_sensor'

        id = Column(
            Integer, ForeignKey(NumericSensor.id, ondelete='CASCADE'), primary_key=True
        )

        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }

        def __init__(self, *args, **kwargs):
            self.min = 0.0
            self.max = 1.0
            self.unit = '%'
            super().__init__(*args, **kwargs)


if 'binary_sensor' not in Base.metadata:

    class BinarySensor(Sensor):
        """
        Models a binary sensor, with a binary boolean value.
        """

        __tablename__ = 'binary_sensor'

        def __init__(self, *args, value=None, **kwargs):
            if isinstance(value, str):
                value = value.lower()

            if str(value).lower() in {'1', 't', 'true', 'on'}:
                value = True
            elif str(value).lower() in {'0', 'f', 'false', 'off'}:
                value = False
            elif value is not None:
                logger.warning('Unsupported value for BinarySensor type: %s', value)
                value = None

            super().__init__(*args, value=value, **kwargs)

        id = Column(
            Integer, ForeignKey(Device.id, ondelete='CASCADE'), primary_key=True
        )
        value = Column(Boolean)

        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }


if 'enum_sensor' not in Base.metadata:

    class EnumSensor(Sensor):
        """
        Models an enum sensor, whose value belongs to a set of pre-defined values.
        """

        __tablename__ = 'enum_sensor'

        id = Column(
            Integer, ForeignKey(Device.id, ondelete='CASCADE'), primary_key=True
        )
        value = Column(String)
        values = Column(JSON)
        """ Possible values for the sensor, as a JSON array. """

        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }


if 'composite_sensor' not in Base.metadata:

    class CompositeSensor(Sensor):
        """
        A composite sensor is a sensor whose value can be mapped to a JSON
        object (either a dictionary or an array)
        """

        __tablename__ = 'composite_sensor'

        id = Column(
            Integer, ForeignKey(Device.id, ondelete='CASCADE'), primary_key=True
        )
        value = Column(JSON)

        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }
