from sqlalchemy import Column, Integer, ForeignKey

from platypush.common.db import is_defined

from .sensors import NumericSensor


if not is_defined('temperature_sensor'):

    class TemperatureSensor(NumericSensor):
        __tablename__ = 'temperature_sensor'

        id = Column(
            Integer, ForeignKey(NumericSensor.id, ondelete='CASCADE'), primary_key=True
        )

        __table_args__ = {'extend_existing': True}
        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }
