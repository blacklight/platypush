from sqlalchemy import Column, Integer, ForeignKey

from platypush.common.db import is_defined

from .sensors import NumericSensor


if not is_defined('steps_sensor'):

    class StepsSensor(NumericSensor):
        """
        A sensor that measures the number of steps taken.
        """

        __tablename__ = 'steps_sensor'

        id = Column(
            Integer, ForeignKey(NumericSensor.id, ondelete='CASCADE'), primary_key=True
        )

        __table_args__ = {'extend_existing': True}
        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }
