from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Float

from platypush.common.db import is_defined

from .devices import Device


if not is_defined('light'):

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
        red = Column(Float)
        green = Column(Float)
        blue = Column(Float)
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

        __table_args__ = {'extend_existing': True}
        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }
