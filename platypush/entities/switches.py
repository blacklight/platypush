from sqlalchemy import Column, Integer, ForeignKey, Boolean, String, JSON

from platypush.common.db import Base

from .devices import Device


if 'switch' not in Base.metadata:

    class Switch(Device):
        __tablename__ = 'switch'

        id = Column(
            Integer, ForeignKey(Device.id, ondelete='CASCADE'), primary_key=True
        )
        state = Column(Boolean)

        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }


if 'enum_switch' not in Base.metadata:

    class EnumSwitch(Device):
        __tablename__ = 'enum_switch'

        id = Column(
            Integer, ForeignKey(Device.id, ondelete='CASCADE'), primary_key=True
        )
        value = Column(String)
        values = Column(JSON)

        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }
