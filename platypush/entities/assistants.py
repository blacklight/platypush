from sqlalchemy import Column, Integer, ForeignKey, Boolean, String

from platypush.common.db import is_defined

from . import Entity


if not is_defined('assistant'):

    class Assistant(Entity):
        """
        Base class for voice assistant entities.
        """

        __tablename__ = 'assistant'

        id = Column(
            Integer, ForeignKey(Entity.id, ondelete='CASCADE'), primary_key=True
        )
        last_query = Column(String)
        last_response = Column(String)
        conversation_running = Column(Boolean)
        is_muted = Column(Boolean, default=False)
        is_detecting = Column(Boolean, default=True)

        __table_args__ = {'extend_existing': True}
        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }
