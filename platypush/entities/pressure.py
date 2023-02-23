from sqlalchemy import Column, Integer, ForeignKey

from platypush.common.db import Base

from .sensors import NumericSensor


if 'pressure_sensor' not in Base.metadata:

    class PressureSensor(NumericSensor):
        """
        A sensor that measures pressure.
        """

        __tablename__ = 'pressure_sensor'

        id = Column(
            Integer, ForeignKey(NumericSensor.id, ondelete='CASCADE'), primary_key=True
        )

        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }
