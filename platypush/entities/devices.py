from sqlalchemy import Column, Integer, ForeignKey

from ._base import Entity


class Device(Entity):
    __tablename__ = 'device'

    id = Column(Integer, ForeignKey(Entity.id, ondelete='CASCADE'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': __tablename__,
    }
