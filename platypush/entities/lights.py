from sqlalchemy import Column, Integer, ForeignKey

from .devices import Device


class Light(Device):
    __tablename__ = 'light'

    id = Column(Integer, ForeignKey(Device.id, ondelete='CASCADE'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': __tablename__,
    }
