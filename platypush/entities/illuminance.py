from sqlalchemy import Column, Integer, ForeignKey

from .devices import entity_types_registry
from .sensors import NumericSensor


if not entity_types_registry.get('IlluminanceSensor'):

    class IlluminanceSensor(NumericSensor):
        __tablename__ = 'illuminance_sensor'

        id = Column(
            Integer, ForeignKey(NumericSensor.id, ondelete='CASCADE'), primary_key=True
        )

        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }

    entity_types_registry['IlluminanceSensor'] = IlluminanceSensor
else:
    IlluminanceSensor = entity_types_registry['IlluminanceSensor']
