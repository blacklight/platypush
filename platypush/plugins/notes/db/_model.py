from uuid import uuid4

from platypush.common.db import Base

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Float,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.schema import PrimaryKeyConstraint

from platypush.common.db import UUID

TABLE_PREFIX = 'notes_'


class NoteCollection(Base):
    """
    Models the notes_collection table, which contains collections of notes.
    """

    __tablename__ = f'{TABLE_PREFIX}collection'
    __table_args__ = (
        UniqueConstraint(
            'external_id', 'plugin', name='note_collection_external_id_plugin_idx'
        ),
    )

    id = Column(UUID, primary_key=True, nullable=False, default=uuid4)
    external_id = Column(String, nullable=False)
    plugin = Column(String, nullable=False)
    title = Column(String, nullable=False, index=True)
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


class Note(Base):
    """
    Models the notes_note table, which contains user notes.
    """

    __tablename__ = f'{TABLE_PREFIX}note'
    __table_args__ = (
        UniqueConstraint('external_id', 'plugin', name='note_external_id_plugin_idx'),
    )

    id = Column(UUID, primary_key=True, nullable=False, default=uuid4)
    external_id = Column(String, nullable=False)
    plugin = Column(String, nullable=False)
    title = Column(String, nullable=False, index=True)
    description = Column(String, nullable=True, index=True)
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
    synced_from = relationship(
        'Note',
        secondary=f"{TABLE_PREFIX}sync_state",
        primaryjoin=f"Note.id == {TABLE_PREFIX}sync_state.c.local_note_id",
        secondaryjoin=f"Note.id == {TABLE_PREFIX}sync_state.c.remote_note_id",
        viewonly=True,
        sync_backref=False,
    )
    synced_to = relationship(
        'Note',
        secondary=f"{TABLE_PREFIX}sync_state",
        primaryjoin=f"Note.id == {TABLE_PREFIX}sync_state.c.remote_note_id",
        secondaryjoin=f"Note.id == {TABLE_PREFIX}sync_state.c.local_note_id",
        viewonly=True,
        sync_backref=False,
    )
    conflict_notes = relationship(
        'Note',
        secondary=f"{TABLE_PREFIX}sync_state",
        primaryjoin=f"Note.id == {TABLE_PREFIX}sync_state.c.conflict_note_id",
        secondaryjoin=f"{TABLE_PREFIX}sync_state.c.local_note_id == Note.id",
        viewonly=True,
        sync_backref=False,
    )
    conflicting_for = relationship(
        'Note',
        secondary=f"{TABLE_PREFIX}sync_state",
        primaryjoin=f"{TABLE_PREFIX}sync_state.c.local_note_id == Note.id",
        secondaryjoin=f"Note.id == {TABLE_PREFIX}sync_state.c.conflict_note_id",
        viewonly=True,
        sync_backref=False,
        uselist=False,
    )


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
    __table_args__ = (
        UniqueConstraint(
            'external_id', 'plugin', name='note_resource_external_id_plugin_idx'
        ),
    )

    id = Column(UUID, primary_key=True, nullable=False, default=uuid4)
    external_id = Column(String, nullable=False)
    plugin = Column(String, nullable=False)
    title = Column(String, nullable=False, index=True)
    filename = Column(String, nullable=False, index=True)
    content_type = Column(String, nullable=True)
    size = Column(Integer, nullable=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    notes = relationship(
        'NoteNoteResource',
        backref='resource',
        cascade='all, delete-orphan',
    )


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


class NoteContentIndex(Base):
    """
    Models the notes_content_index table, which contains full-text search
    indexes for note content.
    """

    __tablename__ = f'{TABLE_PREFIX}content_index'
    __table_args__ = (
        PrimaryKeyConstraint('note_id', 'token', name='note_content_index_pkey'),
    )

    note_id = Column(
        UUID,
        ForeignKey(f'{TABLE_PREFIX}note.id', ondelete='CASCADE'),
        primary_key=True,
        nullable=False,
    )
    token = Column(String, primary_key=True, nullable=False, index=True)
    length = Column(Integer, nullable=False)
    count = Column(Integer, nullable=False, default=1)


class NoteSyncState(Base):
    """
    Models the notes_sync_state table, which contains the synchronization state
    for notes and collections.
    """

    __tablename__ = f'{TABLE_PREFIX}sync_state'
    __table_args__ = (
        PrimaryKeyConstraint(
            'local_note_id', 'remote_note_id', name='note_sync_state_pkey'
        ),
    )

    local_note_id = Column(
        UUID,
        ForeignKey(f'{TABLE_PREFIX}note.id', ondelete='CASCADE'),
        primary_key=True,
        nullable=False,
    )
    remote_note_id = Column(
        UUID,
        ForeignKey(f'{TABLE_PREFIX}note.id', ondelete='CASCADE'),
        primary_key=True,
        nullable=False,
    )
    conflict_note_id = Column(
        UUID,
        ForeignKey(f'{TABLE_PREFIX}note.id', ondelete='SET NULL'),
        nullable=True,
    )

    local_note = relationship(
        'Note',
        foreign_keys=[local_note_id],
    )
    remote_note = relationship(
        'Note',
        foreign_keys=[remote_note_id],
    )
    conflict_note = relationship(
        'Note',
        foreign_keys=[conflict_note_id],
    )


# vim:sw=4:ts=4:et:
