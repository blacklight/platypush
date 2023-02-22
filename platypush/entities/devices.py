from sqlalchemy import Column, Integer, Boolean, ForeignKey

from platypush.common.db import Base

from ._base import Entity


if 'device' not in Base.metadata:

    class Device(Entity):
        """
        Base class to model device entities.
        """

        __tablename__ = 'device'

        id = Column(
            Integer, ForeignKey(Entity.id, ondelete='CASCADE'), primary_key=True
        )
        reachable = Column(Boolean, default=True)

        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }
