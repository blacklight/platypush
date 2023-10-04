from sqlalchemy import Column, Integer, ForeignKey

from platypush.common.db import is_defined

from .three_axis import ThreeAxisSensor


if not is_defined('accelerometer'):

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

        __table_args__ = {'extend_existing': True}
        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }
