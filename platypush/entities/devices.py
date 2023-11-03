from sqlalchemy import Column, Integer, Boolean, ForeignKey

from platypush.common.db import is_defined

from ._base import Entity


if not is_defined('device'):

    class Device(Entity):
        """
        Base class to model device entities.
        """

        __tablename__ = 'device'

        id = Column(
            Integer, ForeignKey(Entity.id, ondelete='CASCADE'), primary_key=True
        )
        reachable = Column(Boolean, default=True)

        __table_args__ = {'extend_existing': True}
        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }
