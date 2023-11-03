from sqlalchemy import Column, Integer, ForeignKey

from platypush.common.db import is_defined

from .dimmers import Dimmer
from .switches import Switch


if not is_defined('volume'):

    class Volume(Dimmer):
        __tablename__ = 'volume'

        id = Column(
            Integer, ForeignKey(Dimmer.id, ondelete='CASCADE'), primary_key=True
        )

        __table_args__ = {'extend_existing': True}
        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }


if not is_defined('muted'):

    class Muted(Switch):
        __tablename__ = 'muted'

        id = Column(
            Integer, ForeignKey(Switch.id, ondelete='CASCADE'), primary_key=True
        )

        __table_args__ = {'extend_existing': True}
        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }
