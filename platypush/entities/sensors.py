import logging

from sqlalchemy import Column, Integer, ForeignKey, Boolean, Numeric, String

from .devices import Device, entity_types_registry

logger = logging.getLogger(__name__)


class Sensor(Device):
    __abstract__ = True


if not entity_types_registry.get('RawSensor'):

    class RawSensor(Sensor):
        __tablename__ = 'raw_sensor'

        id = Column(
            Integer, ForeignKey(Device.id, ondelete='CASCADE'), primary_key=True
        )
        value = Column(String)

        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }

    entity_types_registry['RawSensor'] = RawSensor
else:
    RawSensor = entity_types_registry['RawSensor']


if not entity_types_registry.get('NumericSensor'):

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

    entity_types_registry['NumericSensor'] = NumericSensor
else:
    NumericSensor = entity_types_registry['NumericSensor']


if not entity_types_registry.get('BinarySensor'):

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

    entity_types_registry['BinarySensor'] = BinarySensor
else:
    BinarySensor = entity_types_registry['BinarySensor']
