import datetime

from sqlalchemy import (
    Float,
    Column,
    Integer,
    String,
    DateTime,
    PrimaryKeyConstraint,
    ForeignKey,
)
from sqlalchemy.orm import sessionmaker, scoped_session

from platypush.common.db import declarative_base

Base = declarative_base()
Session = scoped_session(sessionmaker())


class MediaDirectory(Base):
    """Models the MediaDirectory table"""

    __tablename__ = 'MediaDirectory'
    __table_args__ = {'sqlite_autoincrement': True}

    id = Column(Integer, primary_key=True)
    path = Column(String)
    last_indexed_at = Column(DateTime)

    @classmethod
    def build(cls, path, last_indexed_at=None, id=None):
        record = cls()
        record.id = id
        record.path = path
        record.last_indexed_at = last_indexed_at
        return record


class MediaFile(Base):
    """Models the MediaFile table"""

    __tablename__ = 'MediaFile'
    __table_args__ = {'sqlite_autoincrement': True}

    id = Column(Integer, primary_key=True)
    directory_id = Column(
        Integer, ForeignKey('MediaDirectory.id', ondelete='CASCADE'), nullable=False
    )
    path = Column(String, nullable=False, unique=True)
    duration = Column(Float)
    width = Column(Integer)
    height = Column(Integer)
    image = Column(String)
    created_at = Column(DateTime)
    indexed_at = Column(DateTime)

    @classmethod
    def build(cls, directory_id, path, indexed_at=None, id=None, **kwargs):
        record = cls()
        record.id = id
        record.directory_id = directory_id
        record.path = path
        record.indexed_at = indexed_at or datetime.datetime.now()

        for k, v in kwargs.items():
            setattr(record, k, v)

        return record


class MediaToken(Base):
    """Models the MediaToken table"""

    __tablename__ = 'MediaToken'
    __table_args__ = {'sqlite_autoincrement': True}

    id = Column(Integer, primary_key=True)
    token = Column(String, nullable=False, unique=True)

    @classmethod
    def build(cls, token, id=None):
        record = cls()
        record.id = id
        record.token = token
        return record


class MediaFileToken(Base):
    """Models the MediaFileToken table"""

    __tablename__ = 'MediaFileToken'

    file_id = Column(
        Integer, ForeignKey('MediaFile.id', ondelete='CASCADE'), nullable=False
    )
    token_id = Column(
        Integer, ForeignKey('MediaToken.id', ondelete='CASCADE'), nullable=False
    )

    __table_args__ = (PrimaryKeyConstraint(file_id, token_id), {})

    @classmethod
    def build(cls, file_id, token_id, id=None):
        record = cls()
        record.id = id
        record.file_id = file_id
        record.token_id = token_id
        return record


# vim:sw=4:ts=4:et:
