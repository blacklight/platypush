from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Float

from .devices import Device


class Light(Device):
    __tablename__ = 'light'

    id = Column(Integer, ForeignKey(Device.id, ondelete='CASCADE'), primary_key=True)
    on = Column(Boolean)
    brightness = Column(Float)
    saturation = Column(Float)
    hue = Column(Float)
    temperature = Column(Float)
    colormode = Column(String)

    __mapper_args__ = {
        'polymorphic_identity': __tablename__,
    }
