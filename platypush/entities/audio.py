from sqlalchemy import Column, Integer, ForeignKey

from platypush.common.db import Base

from .dimmers import Dimmer
from .switches import Switch


if 'volume' not in Base.metadata:

    class Volume(Dimmer):
        __tablename__ = 'volume'

        id = Column(
            Integer, ForeignKey(Dimmer.id, ondelete='CASCADE'), primary_key=True
        )

        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }


if 'muted' not in Base.metadata:

    class Muted(Switch):
        __tablename__ = 'muted'

        id = Column(
            Integer, ForeignKey(Switch.id, ondelete='CASCADE'), primary_key=True
        )

        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }
