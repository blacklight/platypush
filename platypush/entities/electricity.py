from sqlalchemy import Column, Integer, ForeignKey

from .devices import entity_types_registry
from .sensors import NumericSensor


if not entity_types_registry.get('PowerSensor'):

    class PowerSensor(NumericSensor):
        __tablename__ = 'power_sensor'

        id = Column(
            Integer, ForeignKey(NumericSensor.id, ondelete='CASCADE'), primary_key=True
        )

        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }

    entity_types_registry['PowerSensor'] = PowerSensor
else:
    PowerSensor = entity_types_registry['PowerSensor']


if not entity_types_registry.get('CurrentSensor'):

    class CurrentSensor(NumericSensor):
        __tablename__ = 'current_sensor'

        id = Column(
            Integer, ForeignKey(NumericSensor.id, ondelete='CASCADE'), primary_key=True
        )

        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }

    entity_types_registry['CurrentSensor'] = CurrentSensor
else:
    CurrentSensor = entity_types_registry['CurrentSensor']


if not entity_types_registry.get('VoltageSensor'):

    class VoltageSensor(NumericSensor):
        __tablename__ = 'voltage_sensor'

        id = Column(
            Integer, ForeignKey(NumericSensor.id, ondelete='CASCADE'), primary_key=True
        )

        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }

    entity_types_registry['VoltageSensor'] = VoltageSensor
else:
    VoltageSensor = entity_types_registry['VoltageSensor']


if not entity_types_registry.get('EnergySensor'):

    class EnergySensor(NumericSensor):
        __tablename__ = 'energy_sensor'

        id = Column(
            Integer, ForeignKey(NumericSensor.id, ondelete='CASCADE'), primary_key=True
        )

        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }

    entity_types_registry['EnergySensor'] = EnergySensor
else:
    EnergySensor = entity_types_registry['EnergySensor']
