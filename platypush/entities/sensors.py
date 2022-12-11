import logging

from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    JSON,
    Numeric,
    String,
)

from platypush.common.db import Base

from .devices import Device

logger = logging.getLogger(__name__)


class Sensor(Device):
    __abstract__ = True


if 'raw_sensor' not in Base.metadata:

    class RawSensor(Sensor):
        __tablename__ = 'raw_sensor'

        id = Column(
            Integer, ForeignKey(Device.id, ondelete='CASCADE'), primary_key=True
        )
        value = Column(String)

        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }


if 'numeric_sensor' not in Base.metadata:

    class NumericSensor(Sensor):
        __tablename__ = 'numeric_sensor'

        id = Column(
            Integer, ForeignKey(Device.id, ondelete='CASCADE'), primary_key=True
        )
        value = Column(Numeric)
        min = Column(Numeric)
        max = Column(Numeric)
        unit = Column(String)

        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }


if 'binary_sensor' not in Base.metadata:

    class BinarySensor(Sensor):
        __tablename__ = 'binary_sensor'

        def __init__(self, *args, value=None, **kwargs):
            if isinstance(value, str):
                value = value.lower()

            if value in {True, 1, '1', 't', 'true', 'on'}:
                value = True
            elif value in {False, 0, '0', 'f', 'false', 'off'}:
                value = False
            elif value is not None:
                logger.warning(f'Unsupported value for BinarySensor type: {value}')
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
        __tablename__ = 'enum_sensor'

        id = Column(
            Integer, ForeignKey(Device.id, ondelete='CASCADE'), primary_key=True
        )
        value = Column(String)
        values = Column(JSON)

        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }