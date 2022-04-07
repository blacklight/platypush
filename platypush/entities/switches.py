from sqlalchemy import Column, Integer, ForeignKey, Boolean

from .devices import Device


class Switch(Device):
    __tablename__ = 'switch'

    id = Column(Integer, ForeignKey(Device.id), primary_key=True)
    state = Column(Boolean)

    __mapper_args__ = {
        'polymorphic_identity': __tablename__,
    }

    @classmethod
    @property
    def meta(cls):
        return {
            'icon_class': 'fa-solid fa-light-switch',
        }

    def on(self):
        return self.get_plugin().on(self)

    def off(self):
        return self.get_plugin().off(self)

    def toggle(self):
        return self.get_plugin().toggle(self)
