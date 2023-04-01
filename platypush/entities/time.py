from sqlalchemy import Column, Integer, ForeignKey

from platypush.common.db import Base

from .sensors import NumericSensor


if 'time_duration' not in Base.metadata:

    class TimeDuration(NumericSensor):
        """
        An entity that measures a time duration.
        """

        __tablename__ = 'time_duration'

        id = Column(
            Integer, ForeignKey(NumericSensor.id, ondelete='CASCADE'), primary_key=True
        )

        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }
