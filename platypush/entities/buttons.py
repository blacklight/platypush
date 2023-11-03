import logging

from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
)

from platypush.common.db import is_defined

from .sensors import EnumSensor

logger = logging.getLogger(__name__)


if not is_defined('button'):

    class Button(EnumSensor):
        __tablename__ = 'button'

        id = Column(
            Integer, ForeignKey(EnumSensor.id, ondelete='CASCADE'), primary_key=True
        )

        __table_args__ = {'extend_existing': True}
        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }
