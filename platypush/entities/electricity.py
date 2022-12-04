from sqlalchemy import Column, Integer, ForeignKey

from platypush.common.db import Base

from .sensors import NumericSensor


if 'power_sensor' not in Base.metadata:

    class PowerSensor(NumericSensor):
        __tablename__ = 'power_sensor'

        id = Column(
            Integer, ForeignKey(NumericSensor.id, ondelete='CASCADE'), primary_key=True
        )

        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }


if 'current_sensor' not in Base.metadata:

    class CurrentSensor(NumericSensor):
        __tablename__ = 'current_sensor'

        id = Column(
            Integer, ForeignKey(NumericSensor.id, ondelete='CASCADE'), primary_key=True
        )

        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }


if 'voltage_sensor' not in Base.metadata:

    class VoltageSensor(NumericSensor):
        __tablename__ = 'voltage_sensor'

        id = Column(
            Integer, ForeignKey(NumericSensor.id, ondelete='CASCADE'), primary_key=True
        )

        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }


if 'energy_sensor' not in Base.metadata:

    class EnergySensor(NumericSensor):
        __tablename__ = 'energy_sensor'

        id = Column(
            Integer, ForeignKey(NumericSensor.id, ondelete='CASCADE'), primary_key=True
        )

        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }
