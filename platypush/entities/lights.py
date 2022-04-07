from sqlalchemy import Column, Integer, ForeignKey

from .devices import Device


class Light(Device):
    __tablename__ = 'light'

    id = Column(Integer, ForeignKey(Device.id), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': __tablename__,
    }

    @classmethod
    @property
    def meta(cls):
        return {
            'icon_class': 'fa-solid fa-lightbulb',
        }
