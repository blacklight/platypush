from sqlalchemy import Column, Integer, ForeignKey

from platypush.common.db import Base

from .sensors import NumericSensor


if 'heart_rate_sensor' not in Base.metadata:

    class HeartRateSensor(NumericSensor):
        """
        A sensor that measures the heart rate.
        """

        __tablename__ = 'heart_rate_sensor'

        id = Column(
            Integer, ForeignKey(NumericSensor.id, ondelete='CASCADE'), primary_key=True
        )

        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }
