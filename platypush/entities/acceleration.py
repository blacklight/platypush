from sqlalchemy import Column, Integer, ForeignKey

from platypush.common.db import Base

from .three_axis import ThreeAxisSensor


if 'accelerometer' not in Base.metadata:

    class Accelerometer(ThreeAxisSensor):
        """
        An entity that represents the value of an accelerometer sensor.
        """

        __tablename__ = 'accelerometer'

        id = Column(
            Integer,
            ForeignKey(ThreeAxisSensor.id, ondelete='CASCADE'),
            primary_key=True,
        )

        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }
