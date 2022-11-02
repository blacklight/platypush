from sqlalchemy import Column, Integer, ForeignKey, Numeric, String

from .devices import Device, entity_types_registry


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
