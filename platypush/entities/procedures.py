import logging

from sqlalchemy import (
    Column,
    Enum,
    ForeignKey,
    Integer,
    JSON,
    String,
)

from platypush.common.db import is_defined

from . import Entity

logger = logging.getLogger(__name__)


if not is_defined('procedure'):

    class Procedure(Entity):
        """
        Models a procedure entity.
        """

        __tablename__ = 'procedure'

        id = Column(
            Integer, ForeignKey('entity.id', ondelete='CASCADE'), primary_key=True
        )
        args = Column(JSON, nullable=False, default=[])
        procedure_type = Column(
            Enum('python', 'config', name='procedure_type'), nullable=False
        )
        module = Column(String)
        source = Column(String)
        line = Column(Integer)

        __table_args__ = {'keep_existing': True}
        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }
