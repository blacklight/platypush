from sqlalchemy import (
    Column,
    ForeignKey,
    Float,
    Integer,
)

from platypush.common.db import is_defined

from .devices import Device


if not is_defined('ping_host'):

    class PingHost(Device):
        """
        Entity that maps a generic host that can be pinged.
        """

        __tablename__ = 'ping_host'

        id = Column(
            Integer, ForeignKey(Device.id, ondelete='CASCADE'), primary_key=True
        )

        min = Column(Float)
        max = Column(Float)
        avg = Column(Float)
        mdev = Column(Float)

        __table_args__ = {'extend_existing': True}
        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }
