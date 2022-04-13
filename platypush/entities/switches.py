from sqlalchemy import Column, Integer, ForeignKey, Boolean

from .devices import Device


class Switch(Device):
    __tablename__ = 'switch'

    id = Column(Integer, ForeignKey(Device.id, ondelete='CASCADE'), primary_key=True)
    state = Column(Boolean)

    __mapper_args__ = {
        'polymorphic_identity': __tablename__,
    }
