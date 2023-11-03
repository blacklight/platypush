from sqlalchemy import Column, Integer, ForeignKey

from platypush.common.db import is_defined

from .sensors import NumericSensor


if not is_defined('power_sensor'):

    class PowerSensor(NumericSensor):
        __tablename__ = 'power_sensor'

        id = Column(
            Integer, ForeignKey(NumericSensor.id, ondelete='CASCADE'), primary_key=True
        )

        __table_args__ = {'extend_existing': True}
        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }


if not is_defined('current_sensor'):

    class CurrentSensor(NumericSensor):
        __tablename__ = 'current_sensor'

        id = Column(
            Integer, ForeignKey(NumericSensor.id, ondelete='CASCADE'), primary_key=True
        )

        __table_args__ = {'extend_existing': True}
        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }


if not is_defined('voltage_sensor'):

    class VoltageSensor(NumericSensor):
        __tablename__ = 'voltage_sensor'

        id = Column(
            Integer, ForeignKey(NumericSensor.id, ondelete='CASCADE'), primary_key=True
        )

        __table_args__ = {'extend_existing': True}
        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }


if not is_defined('energy_sensor'):

    class EnergySensor(NumericSensor):
        __tablename__ = 'energy_sensor'

        id = Column(
            Integer, ForeignKey(NumericSensor.id, ondelete='CASCADE'), primary_key=True
        )

        __table_args__ = {'extend_existing': True}
        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }
