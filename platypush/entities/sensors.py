import logging

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
        value = Column(String)
        is_binary = Column(Boolean, default=False)
        """ If ``is_binary`` is ``True``, then ``value`` is a hex string. """
        is_json = Column(Boolean, default=False)
        """
        If ``is_json`` is ``True``, then ``value`` is a JSON-encoded string
        object or array.
        """

        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }


if 'numeric_sensor' not in Base.metadata:

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
