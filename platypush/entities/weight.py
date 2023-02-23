from sqlalchemy import Column, Integer, ForeignKey

from platypush.common.db import Base

from .sensors import NumericSensor


if 'weight_sensor' not in Base.metadata:

    class WeightSensor(NumericSensor):
        """
        A sensor that measures weight.
        """

        __tablename__ = 'weight_sensor'

        id = Column(
            Integer, ForeignKey(NumericSensor.id, ondelete='CASCADE'), primary_key=True
        )

        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }
