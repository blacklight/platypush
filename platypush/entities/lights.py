from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Float

from .devices import Device, entity_types_registry


if not entity_types_registry.get('Light'):

    class Light(Device):
        __tablename__ = 'light'

        id = Column(
            Integer, ForeignKey(Device.id, ondelete='CASCADE'), primary_key=True
        )
        on = Column(Boolean)
        brightness = Column(Float)
        saturation = Column(Float)
        hue = Column(Float)
        temperature = Column(Float)
        x = Column(Float)
        y = Column(Float)
        colormode = Column(String)
        effect = Column(String)
        hue_min = Column(Float)
        hue_max = Column(Float)
        saturation_min = Column(Float)
        saturation_max = Column(Float)
        brightness_min = Column(Float)
        brightness_max = Column(Float)
        temperature_min = Column(Float)
        temperature_max = Column(Float)

        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }

    entity_types_registry['Light'] = Light
else:
    Light = entity_types_registry['Light']
