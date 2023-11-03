from sqlalchemy import Column, Integer, ForeignKey

from platypush.common.db import is_defined

from .sensors import BinarySensor


if not is_defined('presence_sensor'):

    class PresenceSensor(BinarySensor):
        """
        A binary sensor that detects presence.
        """

        __tablename__ = 'presence_sensor'

        id = Column(
            Integer, ForeignKey(BinarySensor.id, ondelete='CASCADE'), primary_key=True
        )

        __table_args__ = {'extend_existing': True}
        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }
