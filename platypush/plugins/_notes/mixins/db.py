from abc import ABC
from contextlib import contextmanager
from threading import Event, RLock
from typing import Any, Dict, Generator

from sqlalchemy import and_
from sqlalchemy.orm import Session

from platypush.common.notes import Note, NoteCollection
from platypush.context import get_plugin
from platypush.plugins.db import DbPlugin
from platypush.utils import utcnow

from .._model import StateDelta
from ..db._model import (
    Note as DbNote,
    NoteCollection as DbNoteCollection,
)
from .index import NotesIndexMixin


class DbMixin(NotesIndexMixin, ABC):  # pylint: disable=too-few-public-methods
    """
    Mixin class for the database synchronization layer.
    """

    _plugin_name: str

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._notes: Dict[Any, Note] = {}
        self._collections: Dict[Any, NoteCollection] = {}
        self._sync_lock = RLock()
        self._db_lock = RLock()
        self._db_initialized = Event()

    @property
    def _db(self) -> DbPlugin:
        """
        Get the database plugin instance for the current context.
        """
        db = get_plugin(DbPlugin)
        assert db is not None, 'Database plugin not found'
        return db

    @contextmanager
    def _get_db_session(self, *args, **kwargs) -> Generator[Session, None, None]:
        """
        Context manager to get a database session.
        """
        with self._db_lock, self._db.get_session(*args, **kwargs) as session:
            yield session

    def _to_db_collection(self, collection: NoteCollection) -> DbNoteCollection:
        """
        Convert a NoteCollection object to a DbNoteCollection object.
        """
        return DbNoteCollection(
            id=collection._db_id,  # pylint:disable=protected-access
            external_id=collection.id,
            plugin=self._plugin_name,
            title=collection.title,
            description=collection.description,
            parent_id=collection.parent.id if collection.parent else None,
            created_at=collection.created_at or utcnow(),
            updated_at=collection.updated_at or utcnow(),
        )

    def _to_db_note(self, note: Note) -> DbNote:
        """
        Convert a Note object to a DbNote object.
        """
        return DbNote(
            id=note._db_id,  # pylint:disable=protected-access
            external_id=note.id,
            plugin=self._plugin_name,
            title=note.title,
            description=note.description,
            content=note.content,
            parent_id=note.parent._db_id if note.parent else None,
            digest=note.digest,
            latitude=note.latitude,
            longitude=note.longitude,
            altitude=note.altitude,
            author=note.author,
            source_name=note.source.name if note.source else None,
            source_url=note.source.url if note.source else None,
            source_app=note.source.app if note.source else None,
            created_at=note.created_at or utcnow(),
            updated_at=note.updated_at or utcnow(),
        )

    def _from_db_note(self, db_note: DbNote) -> Note:
        """
        Convert a DbNote object to a Note object.
        """
        return Note(
            id=db_note.external_id,
            plugin=self._plugin_name,
            title=db_note.title,  # type: ignore[arg-type]
            description=db_note.description,  # type: ignore[arg-type]
            content=db_note.content,  # type: ignore[arg-type]
            parent=(
                self._from_db_collection(db_note.parent)  # type: ignore[arg-type]
                if db_note.parent
                else None
            ),
            digest=db_note.digest,  # type: ignore[arg-type]
            latitude=db_note.latitude,  # type: ignore[arg-type]
            longitude=db_note.longitude,  # type: ignore[arg-type]
            altitude=db_note.altitude,  # type: ignore[arg-type]
            author=db_note.author,  # type: ignore[arg-type]
            source=(
                {  # type: ignore[arg-type]
                    'name': db_note.source_name,
                    'url': db_note.source_url,
                    'app': db_note.source_app,
                }
                if db_note.source_name  # type: ignore[arg-type]
                else None
            ),
            created_at=db_note.created_at,  # type: ignore[arg-type]
            updated_at=db_note.updated_at,  # type: ignore[arg-type]
        )

    def _from_db_collection(self, db_collection: DbNoteCollection) -> NoteCollection:
        """
        Convert a DbNoteCollection object to a NoteCollection object.
        """
        return NoteCollection(
            id=db_collection.external_id,
            plugin=self._plugin_name,
            title=db_collection.title,  # type: ignore[arg-type]
            description=db_collection.description,  # type: ignore[arg-type]
            parent=(
                self._from_db_collection(db_collection.parent)  # type: ignore[arg-type]
                if db_collection.parent
                else None
            ),
            created_at=db_collection.created_at,  # type: ignore[arg-type]
            updated_at=db_collection.updated_at,  # type: ignore[arg-type]
        )

    def _db_fetch_notes(self, session: Session) -> Dict[Any, Note]:
        """
        Fetch notes from the database.
        """
        return {
            note.external_id: self._from_db_note(note)
            for note in session.query(DbNote).filter_by(plugin=self._plugin_name).all()
        }

    def _db_fetch_collections(self, session: Session) -> Dict[Any, NoteCollection]:
        """
        Fetch collections from the database.
        """
        return {
            collection.external_id: self._from_db_collection(collection)
            for collection in session.query(DbNoteCollection)
            .filter_by(plugin=self._plugin_name)
            .all()
        }

    def _db_init(self, force: bool = False) -> None:
        """
        Initialize the database by fetching notes and collections.
        """
        with self._db_lock:
            if self._db_initialized.is_set() and not force:
                return

            with self._get_db_session() as session:
                notes = self._db_fetch_notes(session)
                collections = self._db_fetch_collections(session)

        with self._sync_lock:
            self._notes = notes
            self._collections = collections

    def _db_sync(self, state: StateDelta):
        if state.is_empty():
            return

        with self._get_db_session(autoflush=False) as session:
            # Add new/updated collections
            for collection in [
                *state.collections.added.values(),
                *state.collections.updated.values(),
            ]:
                db_collection = self._to_db_collection(collection)
                session.merge(db_collection)

            # Delete removed collections
            session.query(DbNoteCollection).filter(
                and_(
                    DbNoteCollection.plugin == self._plugin_name,
                    DbNoteCollection.external_id.in_(
                        [
                            collection.id
                            for collection in state.collections.deleted.values()
                        ]
                    ),
                )
            ).delete()

            # Ensure that collections are saved before notes
            session.flush()

            # Add new/updated notes
            for note in [*state.notes.added.values(), *state.notes.updated.values()]:
                db_note = self._to_db_note(note)
                session.merge(db_note)

            # Delete removed notes
            session.query(DbNote).filter(
                and_(
                    DbNote.plugin == self._plugin_name,
                    DbNote.external_id.in_(
                        [note.id for note in state.notes.deleted.values()]
                    ),
                )
            ).delete()

            # Refresh the content index for any new or updated notes
            self._refresh_content_index(
                notes=[*state.notes.added.values(), *state.notes.updated.values()],
                session=session,
            )

            session.commit()

    def _db_clear(self) -> None:
        """
        Clear the database by removing all notes and collections.
        """
        with self._get_db_session() as session:
            session.query(DbNote).filter_by(plugin=self._plugin_name).delete()
            session.query(DbNoteCollection).filter_by(plugin=self._plugin_name).delete()

        with self._sync_lock:
            self._notes.clear()
            self._collections.clear()
