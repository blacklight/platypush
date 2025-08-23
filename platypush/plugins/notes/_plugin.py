import os
import shutil
from datetime import datetime
from threading import Timer
from typing import Any, Dict, List, Optional

from watchdog.observers import Observer

from platypush.bus import Bus
from platypush.common.notes import Note, NoteCollection, NoteContentType, Storable
from platypush.message.event.file import (
    FileSystemEvent,
    FileSystemDeleteEvent,
    FileSystemMovedEvent,
)
from platypush.plugins.file.monitor import EventHandler
from platypush.plugins.file.monitor.entities.resources import MonitoredResource
from platypush.plugins.notes import ApiSettings, BaseNotePlugin, Results
from platypush.plugins.notes._model import StateDelta


# pylint: disable=too-many-ancestors
class NotesPlugin(BaseNotePlugin):
    """
    This plugin provides the ability to manage local notes on the filesystem.

    Specify the directory where the notes are stored in the ``path``
    parameter.

    It can be synchronized with external notes plugins through the
    ``sync_to_plugins`` configuration parameter, which allows you to
    synchronize notes with other plugins that support the same API.
    """

    _api_settings = ApiSettings(
        supports_notes_limit=True,
        supports_notes_offset=True,
        supports_collections_limit=True,
        supports_collections_offset=True,
        supports_search_limit=False,
        supports_search_offset=False,
        supports_search=False,
    )

    _supported_notes_exts = ['md', 'txt', 'rst', 'html']

    def __init__(
        self,
        path: str,
        *args,
        file_extension: str = 'md',
        poll_interval: float = 10.0,
        **kwargs,
    ):
        """
        :param path: The directory where the notes are stored.
        :param file_extension: The file extension for the notes. Defaults to ``md``.
        """
        super().__init__(*args, poll_interval=poll_interval, **kwargs)
        self.path = os.path.abspath(os.path.expanduser(path))
        self.file_extension = file_extension

        self._pending_events: List[FileSystemEvent] = []
        self._event_processor: Optional[Timer] = None
        self._watchdog_bus = Bus()
        self._observer = Observer()
        evt_hndl = EventHandler(
            resource=MonitoredResource(path=self.path, recursive=True),
            bus=self._watchdog_bus,
        )
        self._observer.schedule(evt_hndl, self.path, recursive=True)
        self.logger.info('Notes plugin initialized with notes directory: %s', self.path)

    @classmethod
    def _is_note(cls, path: str) -> bool:
        return any(path.endswith(f'.{ext}') for ext in cls._supported_notes_exts)

    def _id_to_path(self, item_id: Any) -> str:
        """
        Convert an item ID to a path within the notes directory.
        """
        item_id = os.path.expanduser(str(item_id).strip())
        candidate_path = os.path.abspath(
            item_id if os.path.isabs(item_id) else os.path.join(self.path, item_id)
        )

        # Security check: must be inside path (abspath, not realpath, so symlinks OK)
        notes_dir_abs = os.path.abspath(self.path)
        assert (
            os.path.commonpath([candidate_path, notes_dir_abs]) == notes_dir_abs
        ), f'Item ID "{item_id}" is outside the notes directory "{self.path}"'

        return candidate_path

    def _path_to_id(self, path: str) -> Any:
        """
        Convert an item path to an ID relative to the notes directory.
        """
        path = os.path.expanduser(path)
        path = os.path.abspath(
            path if os.path.isabs(path) else os.path.join(self.path, path)
        )

        # Security check: must be inside notes_dir (abspath, not realpath, so symlinks OK)
        notes_dir_abs = os.path.abspath(self.path)
        assert (
            os.path.commonpath([path, notes_dir_abs]) == notes_dir_abs
        ), f'Item path "{path}" is outside the notes directory "{self.path}"'

        return os.path.relpath(path, notes_dir_abs)

    def _note_id_to_path(self, note_id: Any) -> str:
        """
        Convert a note ID to a file path within the notes directory.
        """
        note_id = str(note_id).strip()
        if not self._is_note(note_id):
            note_id += f'.{self.file_extension}'
        return self._id_to_path(note_id)

    def _note_path_to_id(self, path: str) -> Any:
        """
        Convert a file path to a note ID relative to the notes directory.
        """
        path = os.path.expanduser(path)
        if not self._is_note(path):
            path += f'.{self.file_extension}'
        return self._path_to_id(path)

    def _to_note(self, path: str, with_content: bool = False) -> Note:
        """
        Convert a file path to a Note object.
        """
        note_id = self._note_path_to_id(path)
        content = None
        assert os.path.exists(path), f'Note path "{path}" does not exist'

        if with_content:
            with open(path, 'r') as f:
                content = f.read()

        return Note(
            id=note_id,
            plugin=self._plugin_name,
            title=os.path.splitext(os.path.basename(path))[0],
            content=content,
            content_type=NoteContentType.by_extension(os.path.splitext(path)[1][1:]),
            parent=self._fetch_collection(
                os.path.dirname(note_id) if os.path.dirname(note_id) else None
            ),
            created_at=datetime.fromtimestamp(os.path.getctime(path)),
            updated_at=datetime.fromtimestamp(os.path.getmtime(path)),
        )

    def _to_collection(self, path: str) -> NoteCollection:
        """
        Convert a file path to a NoteCollection object.
        """
        collection_id = self._path_to_id(path)
        assert os.path.exists(path), f'Collection path "{path}" does not exist'

        return NoteCollection(
            id=collection_id,
            plugin=self._plugin_name,
            title=os.path.basename(path),
            parent=self._fetch_collection(
                os.path.dirname(collection_id)
                if os.path.dirname(collection_id)
                else None
            ),
            created_at=datetime.fromtimestamp(os.path.getctime(path)),
            updated_at=datetime.fromtimestamp(os.path.getmtime(path)),
        )

    def _fetch_note(self, note_id: Any, *_, **__) -> Optional[Note]:
        try:
            path = self._note_id_to_path(note_id)
            return self._to_note(path, with_content=True)
        except AssertionError:
            return None

    def _fetch_notes(
        self, *_, limit: Optional[int] = None, offset: Optional[int] = None, **__
    ) -> List[Note]:
        notes = []
        for root, _, files in os.walk(self.path):
            for file in files:
                if self._is_note(file):
                    path = os.path.join(root, file)
                    try:
                        note = self._to_note(path, with_content=False)
                        notes.append(note)
                    except AssertionError:
                        continue

        notes.sort(key=lambda n: n.updated_at, reverse=True)
        if limit is not None:
            notes = (
                notes[offset : offset + limit] if offset is not None else notes[:limit]
            )
        elif offset is not None:
            notes = notes[offset:]

        return notes

    def _create_note(
        self,
        title: str,
        content: str,
        *_,
        parent: Optional[Any] = None,
        **__,
    ) -> Note:
        """
        Create a new note with the given title and content.
        """
        title = title.strip()
        filename = title if self._is_note(title) else f'{title}.{self.file_extension}'
        note_id = os.path.join(parent or '', filename)
        path = self._note_id_to_path(note_id)
        content = content or ''
        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, 'w') as f:
            f.write(content)

        return self._to_note(path, with_content=True)

    def _edit_note(
        self,
        note_id: Any,
        *_,
        title: Optional[str] = None,
        content: Optional[str] = None,
        parent: Optional[Any] = None,
        **__,
    ) -> Note:
        """
        Edit an existing note with the given ID.
        """
        note = self._fetch_note(note_id)
        assert note is not None, f'Note with ID "{note_id}" not found'

        if title is not None or parent is not None:
            old_path = self._note_id_to_path(note.id)
            new_parent = parent or (note.parent.id if note.parent else '')
            new_title = title.strip() if title else note.title
            filename = (
                new_title
                if self._is_note(new_title)
                else f'{new_title}.{self.file_extension}'
            )
            note_id = os.path.join(new_parent, filename)
            new_path = self._note_id_to_path(note_id)

            if new_path != old_path:
                os.makedirs(os.path.dirname(new_path), exist_ok=True)
                os.rename(old_path, new_path)
                note.id = note_id
                note.title = new_title

        if content is not None:
            path = self._note_id_to_path(note.id)
            with open(path, 'w') as f:
                f.write(content)

        note.updated_at = datetime.now()
        note.content = content if content is not None else note.content
        return note

    def _delete_note(self, note_id: Any, *_, **__):
        """
        Delete a note with the given ID.
        """
        note = self._fetch_note(note_id)
        assert note is not None, f'Note with ID "{note_id}" not found'

        path = self._note_id_to_path(note.id)
        if not os.path.exists(path):
            raise FileNotFoundError(f'Note file "{path}" does not exist')
        os.remove(path)

    def _fetch_collection(
        self, collection_id: Any, *_, **__
    ) -> Optional[NoteCollection]:
        """
        Fetch a collection by its ID.
        """
        try:
            path = self._id_to_path(collection_id)
            if not os.path.exists(path):
                return None

            return self._to_collection(path)
        except AssertionError:
            return None

    def _fetch_collections(
        self, *_, limit: Optional[int] = None, offset: Optional[int] = None, **__
    ) -> List[NoteCollection]:
        collections = {}
        for root, _, files in os.walk(self.path):
            for file in files:
                if self._is_note(file):
                    path = os.path.dirname(os.path.join(root, file))
                    if path == self.path:
                        continue

                    try:
                        collection = self._to_collection(path)
                        collections[collection.id] = collection
                    except AssertionError:
                        continue

        collections = list(collections.values())
        collections.sort(key=lambda c: c.updated_at, reverse=True)
        if limit is not None:
            collections = (
                collections[offset : offset + limit]
                if offset is not None
                else collections[:limit]
            )
        elif offset is not None:
            collections = collections[offset:]

        return collections

    def _create_collection(
        self,
        title: str,
        *_,
        parent: Optional[Any] = None,
        **__,
    ) -> NoteCollection:
        """
        Create a new collection with the given title.
        """
        collection_id = os.path.join(parent or '', title)
        path = self._id_to_path(collection_id)
        os.makedirs(path, exist_ok=True)
        return self._to_collection(path)

    def _edit_collection(
        self,
        collection_id: Any,
        *_,
        title: Optional[str] = None,
        parent: Optional[Any] = None,
        **__,
    ) -> NoteCollection:
        """
        Edit an existing collection with the given ID.
        """
        collection = self._fetch_collection(collection_id)
        assert collection is not None, f'Collection with ID "{collection_id}" not found'

        if title is not None or parent is not None:
            old_path = self._id_to_path(collection.id)
            new_parent = parent or (collection.parent.id if collection.parent else '')
            new_path = self._id_to_path(
                os.path.join(new_parent, title or collection.title)
            )

            if new_path != old_path:
                os.makedirs(os.path.dirname(new_path), exist_ok=True)
                os.rename(old_path, new_path)
                collection.id = collection_id
                collection.title = os.path.basename(new_path)

        collection.updated_at = datetime.now()
        return collection

    def _delete_collection(self, collection_id: Any, *_: Any, **__: Any):
        """
        Delete a collection with the given ID.
        """
        collection = self._fetch_collection(collection_id)
        assert collection is not None, f'Collection with ID "{collection_id}" not found'

        path = self._id_to_path(collection.id)
        if not os.path.exists(path):
            raise FileNotFoundError(f'Collection path "{path}" does not exist')
        shutil.rmtree(path)

    def _search(self, *_, **__) -> Results:
        raise NotImplementedError(
            'Search is not implemented in the Local Notes API. '
            'Fallback on the internal database search instead.'
        )

    def _infer_id(self, item: Storable) -> Optional[Any]:
        if isinstance(item, Note):
            return self._note_path_to_id(item.path.lstrip("/"))
        if isinstance(item, NoteCollection):
            return self._path_to_id(item.path.lstrip("/"))
        return item.id

    def _poll_events(self, timeout: Optional[float] = 1.0):
        """
        Poll for file system events in the notes directory.
        """
        if not self._observer.is_alive():
            self._observer.start()

        while not self.should_stop():
            evt: Optional[FileSystemEvent] = self._watchdog_bus.get(timeout=timeout)  # type: ignore
            if evt is None:
                continue

            with self._sync_lock:
                if self._event_processor is None:
                    self._event_processor = Timer(
                        self.poll_interval or 1.0, self._process_sync_events
                    )
                    self._event_processor.start()

                self._pending_events.append(evt)

    def _process_sync_events(self):
        """
        Timed function to process pending file system events.
        """
        try:
            with self._sync_lock:
                state_delta = self._to_state_delta(self._pending_events)
                if state_delta.is_empty():
                    return

                self._apply_state_delta(state_delta)
                self._db_sync(state_delta)
                self._last_local_sync_time = datetime.fromtimestamp(
                    state_delta.latest_updated_at
                )
                self._pending_events.clear()
                self._process_events(state_delta)
        finally:
            if self._event_processor:
                self._event_processor.cancel()
                self._event_processor = None

    def _apply_state_delta(self, state_delta: StateDelta):
        for collection in [
            *state_delta.collections.added.values(),
            *state_delta.collections.updated.values(),
        ]:
            self._collections[collection.id] = collection
        for collection_id in state_delta.collections.deleted:
            self._collections.pop(collection_id, None)
        for note in [
            *state_delta.notes.added.values(),
            *state_delta.notes.updated.values(),
        ]:
            self._notes[note.id] = note
        for note_id in state_delta.notes.deleted:
            self._notes.pop(note_id, None)

    def _to_state_delta(self, events: List[FileSystemEvent]) -> StateDelta:
        """
        Calculates the state delta from file system events.
        """
        notes: Dict[str, Note] = {}
        prev_notes: Dict[str, Note] = {}

        for event in events:
            path = event.args.get("path")
            if (
                not path
                or
                # Skip directory events
                event.args.get("is_directory", False)
                or
                # Skip events for unsupported note extensions
                not any(path.endswith(f'.{ext}') for ext in self._supported_notes_exts)
            ):
                continue

            note_id = self._note_path_to_id(path)
            if self._notes.get(note_id):
                prev_notes[note_id] = self._notes[note_id]

            # Handle file move events
            if isinstance(event, FileSystemMovedEvent):
                new_path = event.args.get("new_path")
                assert new_path
                note_id = self._note_path_to_id(new_path)
                notes[note_id] = self._to_note(new_path, with_content=True)
            # Handle file creation or modification
            elif not isinstance(event, FileSystemDeleteEvent):
                notes[note_id] = self._to_note(path, with_content=True)

        collections = {
            note.parent.id: note.parent for note in notes.values() if note.parent
        }

        prev_collections = {
            collection.id: self._collections[collection.id]
            for collection in collections.values()
            if collection.id in self._collections
        }

        return self._get_state_delta(
            previous_notes=prev_notes,
            previous_collections=prev_collections,
            notes=notes,
            collections=collections,
            filter_by_latest_updated_at=False,
        )

    def main(self):
        if not self.poll_interval:
            self.wait_stop()
            return

        try:
            self.sync()
        except Exception as e:
            raise RuntimeError(
                'Failed to perform initial sync with the notes directory'
            ) from e

        try:
            self._poll_events()
        except KeyboardInterrupt:
            self.logger.info('KeyboardInterrupt received, stopping the notes plugin')
        finally:
            self._observer.stop()
            self._observer.join()
            self._watchdog_bus.stop()
            self.logger.info('Notes plugin stopped')
            self.stop_remote_sync()
            self.wait_stop(self.poll_interval)


# vim:sw=4:ts=4:et:
