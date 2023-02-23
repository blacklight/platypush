from sqlalchemy import Column, Integer, ForeignKey

from platypush.common.db import Base

from .sensors import BinarySensor


if 'presence_sensor' not in Base.metadata:

    class PressureSensor(BinarySensor):
        """
        A binary sensor that detects presence.
        """

        __tablename__ = 'presence_sensor'

        id = Column(
            Integer, ForeignKey(BinarySensor.id, ondelete='CASCADE'), primary_key=True
        )

        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }
