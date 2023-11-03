import logging

from sqlalchemy import Column, ForeignKey, Integer, String

from platypush.common.db import is_defined

from . import Entity

logger = logging.getLogger(__name__)


if not is_defined('variable'):

    class Variable(Entity):
        """
        Models a variable entity.
        """

        __tablename__ = 'variable'

        id = Column(
            Integer, ForeignKey('entity.id', ondelete='CASCADE'), primary_key=True
        )
        value = Column(String)

        __table_args__ = {'keep_existing': True}
        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }
