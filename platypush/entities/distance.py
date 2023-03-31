from sqlalchemy import Column, Integer, ForeignKey

from platypush.common.db import Base

from .sensors import NumericSensor


if 'distance_sensor' not in Base.metadata:

    class DistanceSensor(NumericSensor):
        """
        This class models distance sensors.
        """

        __tablename__ = 'distance_sensor'

        id = Column(
            Integer, ForeignKey(NumericSensor.id, ondelete='CASCADE'), primary_key=True
        )

        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }
