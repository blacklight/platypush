from sqlalchemy import Column, Integer, ForeignKey

from platypush.common.db import Base

from .sensors import NumericSensor


if 'humidity_sensor' not in Base.metadata:

    class HumiditySensor(NumericSensor):
        """
        A sensor that measures humidity.
        """

        __tablename__ = 'humidity_sensor'

        id = Column(
            Integer, ForeignKey(NumericSensor.id, ondelete='CASCADE'), primary_key=True
        )

        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }


if 'dew_point_sensor' not in Base.metadata:

    class DewPointSensor(NumericSensor):
        """
        A sensor that measures the dew point.
        """

        __tablename__ = 'dew_point_sensor'

        id = Column(
            Integer, ForeignKey(NumericSensor.id, ondelete='CASCADE'), primary_key=True
        )

        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }
