from sqlalchemy import Column, Integer, ForeignKey

from platypush.common.db import Base

from .three_axis import ThreeAxisSensor


if 'magnetometer' not in Base.metadata:

    class Magnetometer(ThreeAxisSensor):
        """
        An entity that represents the value of a magnetometer.
        """

        __tablename__ = 'magnetometer'

        id = Column(
            Integer,
            ForeignKey(ThreeAxisSensor.id, ondelete='CASCADE'),
            primary_key=True,
        )

        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }
