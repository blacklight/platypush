import logging

from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
)

from platypush.common.db import Base

from .sensors import EnumSensor

logger = logging.getLogger(__name__)


if 'button' not in Base.metadata:

    class Button(EnumSensor):
        __tablename__ = 'button'

        id = Column(
            Integer, ForeignKey(EnumSensor.id, ondelete='CASCADE'), primary_key=True
        )

        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }
