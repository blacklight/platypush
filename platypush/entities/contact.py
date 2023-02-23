from sqlalchemy import Column, Integer, ForeignKey

from platypush.common.db import Base

from .sensors import BinarySensor


if 'contact_sensor' not in Base.metadata:

    class ContactSensor(BinarySensor):
        """
        A binary sensor that detects contact.
        """

        __tablename__ = 'contact_sensor'

        id = Column(
            Integer, ForeignKey(BinarySensor.id, ondelete='CASCADE'), primary_key=True
        )

        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }
