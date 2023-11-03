from sqlalchemy import Column, Integer, ForeignKey, Boolean, String, JSON

from platypush.common.db import is_defined

from .devices import Device


if not is_defined('switch'):

    class Switch(Device):
        __tablename__ = 'switch'

        id = Column(
            Integer, ForeignKey(Device.id, ondelete='CASCADE'), primary_key=True
        )
        state = Column(Boolean)

        __table_args__ = {'extend_existing': True}
        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }


if not is_defined('enum_switch'):

    class EnumSwitch(Device):
        __tablename__ = 'enum_switch'

        id = Column(
            Integer, ForeignKey(Device.id, ondelete='CASCADE'), primary_key=True
        )
        value = Column(String)
        values = Column(JSON)

        __table_args__ = {'extend_existing': True}
        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }
