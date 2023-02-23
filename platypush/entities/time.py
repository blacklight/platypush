from sqlalchemy import Column, Integer, ForeignKey

from platypush.common.db import Base

from .sensors import NumericSensor


if 'time_duration_sensor' not in Base.metadata:

    class TimeDurationSensor(NumericSensor):
        """
        A sensor that measures a time duration.
        """

        __tablename__ = 'time_duration_sensor'

        id = Column(
            Integer, ForeignKey(NumericSensor.id, ondelete='CASCADE'), primary_key=True
        )

        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }
