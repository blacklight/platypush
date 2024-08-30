import logging
from enum import Enum

from sqlalchemy import (
    Column,
    Enum as DbEnum,
    ForeignKey,
    Integer,
    JSON,
    String,
)

from platypush.common.db import is_defined

from . import Entity

logger = logging.getLogger(__name__)


class ProcedureType(Enum):
    PYTHON = 'python'
    CONFIG = 'config'
    DB = 'db'


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
            DbEnum(
                *[m.value for m in ProcedureType.__members__.values()],
                name='procedure_type',
                create_constraint=True,
                validate_strings=True,
            ),
            nullable=False,
        )
        module = Column(String)
        source = Column(String)
        line = Column(Integer)
        actions = Column(JSON)

        __table_args__ = {'keep_existing': True}
        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }
