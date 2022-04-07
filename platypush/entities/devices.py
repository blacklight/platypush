from sqlalchemy import Column, Integer, ForeignKey

from ._base import Entity


class Device(Entity):
    __tablename__ = 'device'

    id = Column(Integer, ForeignKey(Entity.id), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': __tablename__,
    }

    @property
    def _meta(self):
        return {
            **super()._meta,
            'icon_class': 'fa-solid fa-gear',
        }
