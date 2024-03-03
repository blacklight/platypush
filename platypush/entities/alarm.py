from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, JSON, String

from platypush.common.db import is_defined

from . import Entity


if not is_defined('alarm'):

    class Alarm(Entity):
        """
        Alarm entity model.
        """

        __tablename__ = 'alarm'

        id = Column(
            Integer, ForeignKey(Entity.id, ondelete='CASCADE'), primary_key=True
        )

        when = Column(String, nullable=False)
        next_run = Column(Float, nullable=True)
        enabled = Column(Boolean, nullable=False, default=True)
        state = Column(String, nullable=False, default='UNKNOWN')
        media = Column(String, nullable=True)
        media_plugin = Column(String, nullable=True)
        media_repeat = Column(Boolean, nullable=False, default=True)
        audio_volume = Column(Integer, nullable=True)
        snooze_interval = Column(Integer, nullable=True)
        dismiss_interval = Column(Integer, nullable=True)
        actions = Column(JSON, nullable=True)
        static = Column(Boolean, nullable=False, default=False)
        condition_type = Column(String, nullable=False)

        __table_args__ = {'extend_existing': True}
        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }
