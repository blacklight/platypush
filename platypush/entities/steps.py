from sqlalchemy import Column, Integer, ForeignKey

from platypush.common.db import Base

from .sensors import NumericSensor


if 'steps_sensor' not in Base.metadata:

    class StepsSensor(NumericSensor):
        """
        A sensor that measures the number of steps taken.
        """

        __tablename__ = 'steps_sensor'

        id = Column(
            Integer, ForeignKey(NumericSensor.id, ondelete='CASCADE'), primary_key=True
        )

        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }
