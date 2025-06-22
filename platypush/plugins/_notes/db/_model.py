from uuid import uuid4

from sqlalchemy import (
    UUID,
    Column,
    DateTime,
    ForeignKey,
    Float,
    Index,
    Integer,
    String,
)
from sqlalchemy.orm import relationship
from sqlalchemy.schema import PrimaryKeyConstraint

from platypush.common.db import Base

TABLE_PREFIX = 'notes_'


class NoteCollection(Base):
    """
    Models the notes_collection table, which contains collections of notes.
    """

    __tablename__ = f'{TABLE_PREFIX}collection'

    id = Column(UUID, primary_key=True, nullable=False, default=uuid4)
    external_id = Column(String, nullable=False)
    plugin = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    parent_id = Column(
        UUID,
        ForeignKey(
            f'{TABLE_PREFIX}collection.id',
            ondelete='CASCADE',
        ),
        nullable=True,
    )
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

    parent = relationship(
        'NoteCollection', remote_side=[id], foreign_keys=[parent_id], backref='children'
    )
    Index('note_collection_external_id_plugin_idx', external_id, plugin, unique=True)


class Note(Base):
    """
    Models the notes_note table, which contains user notes.
    """

    __tablename__ = f'{TABLE_PREFIX}note'

    id = Column(UUID, primary_key=True, nullable=False, default=uuid4)
    external_id = Column(String, nullable=False)
    plugin = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    content = Column(String, nullable=True)
    parent_id = Column(
        UUID,
        ForeignKey(
            f'{TABLE_PREFIX}collection.id',
            ondelete='CASCADE',
        ),
        nullable=True,
    )
    digest = Column(String, nullable=True, index=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    altitude = Column(Float, nullable=True)
    author = Column(String, nullable=True)
    source_name = Column(String, nullable=True, index=True)
    source_url = Column(String, nullable=True, index=True)
    source_app = Column(String, nullable=True, index=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

    parent = relationship(
        'NoteCollection',
        remote_side=[NoteCollection.id],
        foreign_keys=[parent_id],
        backref='notes',
    )

    tags = relationship('NoteTag', backref='note', cascade='all, delete-orphan')
    resources = relationship(
        'NoteNoteResource',
        backref='note',
        cascade='all, delete-orphan',
    )

    Index('note_external_id_plugin_idx', external_id, plugin, unique=True)


class NoteTag(Base):
    """
    Models the notes_tag table, which contains tags for notes.
    """

    __tablename__ = f'{TABLE_PREFIX}tag'
    __table_args__ = (PrimaryKeyConstraint('note_id', 'tag', name='note_tag_pkey'),)

    note_id = Column(
        UUID,
        ForeignKey(f'{TABLE_PREFIX}note.id'),
        primary_key=True,
        nullable=False,
    )
    tag = Column(String, primary_key=True, nullable=False)


class NoteResource(Base):
    """
    Models the notes_resource table, which contains resources associated with notes.
    """

    __tablename__ = f'{TABLE_PREFIX}resource'

    id = Column(UUID, primary_key=True, nullable=False, default=uuid4)
    external_id = Column(String, nullable=False)
    plugin = Column(String, nullable=False)
    title = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    content_type = Column(String, nullable=True)
    size = Column(Integer, nullable=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    notes = relationship(
        'NoteNoteResource',
        backref='resource',
        cascade='all, delete-orphan',
    )

    Index('note_resource_external_id_plugin_idx', external_id, plugin, unique=True)


class NoteNoteResource(Base):
    """
    Models the notes_note_resource table, which associates notes with resources.
    """

    __tablename__ = f'{TABLE_PREFIX}note_resource'
    __table_args__ = (
        PrimaryKeyConstraint('note_id', 'resource_id', name='note_resource_pkey'),
    )

    note_id = Column(
        UUID,
        ForeignKey(f'{TABLE_PREFIX}note.id', ondelete='CASCADE'),
        primary_key=True,
        nullable=False,
    )
    resource_id = Column(
        UUID,
        ForeignKey(f'{TABLE_PREFIX}resource.id', ondelete='CASCADE'),
        primary_key=True,
        nullable=False,
    )


# vim:sw=4:ts=4:et:
