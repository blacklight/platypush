from sqlalchemy import Column, Integer, ForeignKey, Float

from .devices import Device, entity_types_registry


if not entity_types_registry.get('Dimmer'):

    class Dimmer(Device):
        __tablename__ = 'dimmer'

        id = Column(
            Integer, ForeignKey(Device.id, ondelete='CASCADE'), primary_key=True
        )
        min = Column(Float)
        max = Column(Float)
        step = Column(Float, default=1.0)
        value = Column(Float)

        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }

    entity_types_registry['Dimmer'] = Dimmer
else:
    Dimmer = entity_types_registry['Dimmer']
