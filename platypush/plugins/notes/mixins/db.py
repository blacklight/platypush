from abc import ABC
from contextlib import contextmanager
from logging import Logger
from threading import Event, RLock
from typing import Any, Collection, Dict, Generator, List, Optional, Set, Union

from sqlalchemy import and_
from sqlalchemy.orm import Mapped, Session

from platypush.common.notes import Note, NoteCollection, NoteSource
from platypush.context import get_plugin
from platypush.plugins.db import DbPlugin
from platypush.utils import utcnow

from .._model import StateDelta
from ..db._model import (
    Note as DbNote,
    NoteCollection as DbNoteCollection,
    NoteSyncState as DbNoteSyncState,
)
from .index import NotesIndexMixin


class DbMixin(NotesIndexMixin, ABC):  # pylint: disable=too-few-public-methods
    """
    Mixin class for the database synchronization layer.
    """

    logger: Logger

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

    @property
    def _notes_by_path(self) -> Dict[str, Note]:
        """
        Get a dictionary of notes indexed by their path.
        """
        return {
            note.path: note for note in self._notes.values() if note.path is not None
        }

    @property
    def _collections_by_path(self) -> Dict[str, NoteCollection]:
        """
        Get a dictionary of collections indexed by their path.
        """
        return {
            collection.path: collection
            for collection in self._collections.values()
            if collection.path is not None
        }

    def _to_db_collection(
        self,
        collection: NoteCollection,
        _visited: Optional[Dict[Any, DbNoteCollection]] = None,
    ) -> DbNoteCollection:
        """
        Convert a NoteCollection object to a DbNoteCollection object.
        """
        _visited = _visited or {}
        db_id = collection._db_id
        if db_id in _visited:
            return _visited[db_id]

        db_record = DbNoteCollection(
            id=db_id,
            external_id=collection.id,
            plugin=collection.plugin or self._plugin_name,
            title=collection.title,
            description=collection.description,
            created_at=collection.created_at or utcnow(),
            updated_at=collection.updated_at or utcnow(),
        )

        _visited[db_id] = db_record
        parent = (
            self._to_db_collection(collection.parent, _visited=_visited)  # type: ignore[arg-type]
            if collection.parent
            else None
        )

        if parent and parent.id != db_record.id:  # type: ignore[union-attr]
            db_record.parent_id = parent.id

        return db_record

    def _to_db_note(
        self, note: Note, _visited: Optional[Dict[Any, DbNote]] = None
    ) -> DbNote:
        """
        Convert a Note object to a DbNote object.
        """
        _visited = _visited or {}
        if note._db_id in _visited:  # pylint:disable=protected-access
            return _visited[note._db_id]

        db_note = DbNote(
            **{
                **{
                    k: getattr(note, k)
                    for k, v in DbNote.__dict__.items()
                    if isinstance(v, Mapped)
                    and hasattr(note, k)
                    and k
                    not in {
                        'id',
                        'parent',
                        'synced_from',
                        'synced_to',
                        'conflict_notes',
                        'conflicting_for',
                    }
                },
                'id': note._db_id,  # pylint:disable=protected-access
                'external_id': note.id,
                'plugin': note.plugin or self._plugin_name,
                'tags': list(note.tags or []),
                'parent_id': (
                    self._to_db_collection(note.parent).id if note.parent else None
                ),
                'source_name': note.source.name if note.source else None,
                'source_url': note.source.url if note.source else None,
                'source_app': note.source.app if note.source else None,
                'created_at': note.created_at or utcnow(),
                'updated_at': note.updated_at or utcnow(),
            },
        )

        _visited[note._db_id] = db_note  # pylint:disable=protected-access
        db_note.synced_from = [
            DbNoteSyncState(
                local_note_id=note._db_id,  # pylint: disable=protected-access
                remote_note_id=synced_note._db_id,  # pylint: disable=protected-access
                conflict_note_id=next(
                    iter(
                        [
                            conflict_note._db_id  # pylint: disable=protected-access
                            for conflict_note in note.conflict_notes
                            if conflict_note._db_id  # pylint: disable=protected-access
                            == synced_note._db_id  # pylint: disable=protected-access
                        ]
                    ),
                    None,
                ),
            )
            for synced_note in note.synced_from
        ]

        db_note.conflict_notes = [
            _visited.get(
                # pylint: disable=protected-access
                conflict_note._db_id,
                self._to_db_note(conflict_note, _visited=_visited),
            )
            for conflict_note in note.conflict_notes
        ]

        return db_note

    def _from_db_note(
        self, db_note: DbNote, _visited: Optional[Dict[Any, Note]] = None
    ) -> Note:
        """
        Convert a DbNote object to a Note object.
        """
        _visited = _visited or {}
        if db_note.id in _visited:
            return _visited[db_note.id]

        note = Note(
            **{
                **{
                    k: getattr(db_note, k)
                    for k in Note.__dataclass_fields__
                    if not k.startswith('_') and hasattr(db_note, k)
                },
                'id': db_note.external_id,
                'parent': (
                    self._from_db_collection(db_note.parent)  # type: ignore[arg-type]
                    if db_note.parent
                    else None
                ),
                'source': (
                    NoteSource(
                        name=db_note.source_name,  # type: ignore[arg-type]
                        url=db_note.source_url,  # type: ignore[arg-type]
                        app=db_note.source_app,  # type: ignore[arg-type]
                    )
                    if bool(db_note.source_name)
                    else None
                ),
            }
        )

        _visited[db_note.id] = note
        note.synced_from = [
            self._from_db_note(n, _visited=_visited)
            for n in getattr(db_note, 'synced_from', [])
        ]

        note.synced_to = [
            self._from_db_note(n, _visited=_visited)
            for n in getattr(db_note, 'synced_to', [])
        ]

        note.conflict_notes = [
            self._from_db_note(conflict_note, _visited=_visited)
            for conflict_note in getattr(db_note, 'conflict_notes', [])
        ]

        note.conflicting_for = (
            self._from_db_note(db_note.conflicting_for, _visited=_visited)
            if db_note.conflicting_for
            else None
        )

        return note

    def _from_db_collection(self, db_collection: DbNoteCollection) -> NoteCollection:
        """
        Convert a DbNoteCollection object to a NoteCollection object.
        """
        return NoteCollection(
            **{
                **{
                    k: getattr(db_collection, k)
                    for k in NoteCollection.__dataclass_fields__
                    if not k.startswith('_') and hasattr(db_collection, k)
                },
                'id': db_collection.external_id,
                'parent': (
                    self._from_db_collection(db_collection.parent)  # type: ignore[arg-type]
                    if db_collection.parent
                    else None
                ),
            },
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

    # pylint: disable=protected-access
    def _fold_records(
        self,
        records: Collection[Union[Note, NoteCollection]],
        visited: Optional[Set[Any]] = None,
    ) -> Generator[List[Union[Note, NoteCollection]], None, None]:
        """
        Fold records in a list of lists to ensure that parent records are
        always synced before their children.
        """
        cur_records: Dict[Any, Union[Note, NoteCollection]] = {}
        visited = visited or set()

        for record in records:
            while record:
                if record._db_id in visited:
                    break

                if record.parent is None or record.parent._db_id in visited:
                    cur_records[record._db_id] = record
                    visited.add(record._db_id)
                    break

                record = record.parent

            if isinstance(record, Note):
                sync_notes = {
                    **{note._db_id: note for note in record.synced_from},
                    **{note._db_id: note for note in record.synced_to},
                    **{note._db_id: note for note in record.conflict_notes},
                }

                cur_records.update(sync_notes)
                visited.update(sync_notes.keys())

        if cur_records:
            yield list(cur_records.values())
            next_records = {
                record._db_id: record
                for record in records
                if record._db_id not in visited and record._db_id not in cur_records
            }
            yield from self._fold_records(next_records.values(), visited)

    def _db_sync(self, state: StateDelta):
        if state.is_empty():
            return

        self.logger.debug('Starting DB sync for %s', self._plugin_name)

        with self._get_db_session(autoflush=False) as session:
            updated_collections = {
                collection.id: collection
                for collection in [
                    *state.collections.added.values(),
                    *state.collections.updated.values(),
                    *[
                        note.parent
                        for note in state.notes.added.values()
                        if note.parent
                    ],
                    *[
                        note.parent
                        for note in state.notes.updated.values()
                        if note.parent
                    ],
                ]
            }

            self.logger.debug("Updating %d collections", len(updated_collections))

            # Add new/updated collections
            for collections in self._fold_records(updated_collections.values()):
                for collection in collections:
                    db_collection = self._to_db_collection(collection)  # type: ignore[arg-type]
                    session.merge(db_collection)

            self.logger.debug("Deleting %d collections", len(state.collections.deleted))

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

            self.logger.debug(
                "Updating %d notes", len(state.notes.added) + len(state.notes.updated)
            )

            # Add new/updated notes
            for notes in self._fold_records(
                [
                    *state.notes.added.values(),
                    *state.notes.updated.values(),
                ]
            ):
                for note in notes:
                    if isinstance(note, NoteCollection):
                        continue

                    db_note = self._to_db_note(note)  # type: ignore[arg-type]
                    session.merge(db_note)

            self.logger.debug("Deleting %d notes", len(state.notes.deleted))

            # Delete removed notes
            session.query(DbNote).filter(
                and_(
                    DbNote.plugin == self._plugin_name,
                    DbNote.external_id.in_(
                        [note.id for note in state.notes.deleted.values()]
                    ),
                )
            ).delete()

            self.logger.debug("Refreshing content index")

            # Refresh the content index for any new or updated notes
            self._refresh_content_index(
                notes=[*state.notes.added.values(), *state.notes.updated.values()],
                session=session,
            )

            session.flush()
            session.commit()

        self.logger.debug("DB sync complete")

    def _db_clear(self) -> None:
        """
        Clear the database by removing all notes and collections.
        """
        with self._get_db_session() as session:
            session.query(DbNote).filter_by(plugin=self._plugin_name).delete()
            session.query(DbNoteCollection).filter_by(plugin=self._plugin_name).delete()
            session.commit()

        with self._sync_lock:
            self._notes.clear()
            self._collections.clear()
