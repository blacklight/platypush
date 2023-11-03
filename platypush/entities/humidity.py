from sqlalchemy import Column, Integer, ForeignKey

from platypush.common.db import is_defined

from .sensors import NumericSensor


if not is_defined('humidity_sensor'):

    class HumiditySensor(NumericSensor):
        """
        A sensor that measures humidity.
        """

        __tablename__ = 'humidity_sensor'

        id = Column(
            Integer, ForeignKey(NumericSensor.id, ondelete='CASCADE'), primary_key=True
        )

        __table_args__ = {'extend_existing': True}
        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }


if not is_defined('dew_point_sensor'):

    class DewPointSensor(NumericSensor):
        """
        A sensor that measures the dew point.
        """

        __tablename__ = 'dew_point_sensor'

        id = Column(
            Integer, ForeignKey(NumericSensor.id, ondelete='CASCADE'), primary_key=True
        )

        __table_args__ = {'extend_existing': True}
        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }
