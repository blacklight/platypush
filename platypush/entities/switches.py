from sqlalchemy import Column, Integer, ForeignKey, Boolean, String, JSON

from .devices import Device, entity_types_registry


if not entity_types_registry.get('Switch'):

    class Switch(Device):
        __tablename__ = 'switch'

        id = Column(
            Integer, ForeignKey(Device.id, ondelete='CASCADE'), primary_key=True
        )
        state = Column(Boolean)

        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }

    entity_types_registry['Switch'] = Switch
else:
    Switch = entity_types_registry['Switch']


if not entity_types_registry.get('EnumSwitch'):

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

    entity_types_registry['EnumSwitch'] = EnumSwitch
else:
    EnumSwitch = entity_types_registry['EnumSwitch']
