from sqlalchemy import Column, Integer, ForeignKey

from .devices import entity_types_registry
from .sensors import NumericSensor


if not entity_types_registry.get('TemperatureSensor'):

    class TemperatureSensor(NumericSensor):
        __tablename__ = 'temperature_sensor'

        id = Column(
            Integer, ForeignKey(NumericSensor.id, ondelete='CASCADE'), primary_key=True
        )

        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }

    entity_types_registry['TemperatureSensor'] = TemperatureSensor
else:
    TemperatureSensor = entity_types_registry['TemperatureSensor']
