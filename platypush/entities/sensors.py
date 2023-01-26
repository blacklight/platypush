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
    __abstract__ = True

    def __init__(self, *args, is_read_only=True, **kwargs):
        super().__init__(*args, is_read_only=is_read_only, **kwargs)


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
        value = Column(Float)
        min = Column(Float)
        max = Column(Float)
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

            if value in {True, 1, '1', 't', 'true', 'on', 'ON'}:
                value = True
            elif value in {False, 0, '0', 'f', 'false', 'off', 'OFF'}:
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


if 'multi_value_sensor' not in Base.metadata:

    class MultiValueSensor(Sensor):
        __tablename__ = 'multi_value_sensor'

        id = Column(
            Integer, ForeignKey(Device.id, ondelete='CASCADE'), primary_key=True
        )
        value = Column(JSON)

        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }
