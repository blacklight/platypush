from abc import ABC, abstractmethod
from datetime import datetime
from threading import RLock
from time import time
from typing import Any, Dict, Iterable, Optional, Type

from platypush.common.notes import Note, NoteCollection, NoteSource
from platypush.context import Variable
from platypush.message.event.notes import (
    BaseNoteEvent,
    NoteCreatedEvent,
    NoteUpdatedEvent,
    NoteDeletedEvent,
    CollectionCreatedEvent,
    CollectionUpdatedEvent,
    CollectionDeletedEvent,
)
from platypush.plugins import RunnablePlugin, action
from platypush.utils import get_plugin_name_by_class


class BaseNotePlugin(RunnablePlugin, ABC):
    """
    Base class for note-taking plugins.
    """

    def __init__(self, *args, poll_interval: float = 300, **kwargs):
        """
        :param poll_interval: Poll interval in seconds to check for updates (default: 300).
            If set to zero or null, the plugin will not poll for updates,
            and events will be generated only when you manually call :meth:`.sync`.
        """
        super().__init__(*args, poll_interval=poll_interval, **kwargs)
        self._notes: Dict[Any, Note] = {}
        self._collections: Dict[Any, NoteCollection] = {}
        self._notes_lock = RLock()
        self._collections_lock = RLock()
        self._sync_lock = RLock()
        self.__last_sync_time: Optional[datetime] = None

    @property
    def _last_sync_time_var(self) -> Variable:
        """
        Variable name for the last sync time.
        """
        return Variable(
            f'_LAST_ITEMS_SYNC_TIME[{get_plugin_name_by_class(self.__class__)}]'
        )

    @property
    def _last_sync_time(self) -> Optional[datetime]:
        """
        Get the last sync time from the variable.
        """
        if not self.__last_sync_time:
            t = self._last_sync_time_var.get()
            self.__last_sync_time = datetime.fromtimestamp(float(t)) if t else None

        return self.__last_sync_time

    @_last_sync_time.setter
    def _last_sync_time(self, value: Optional[datetime]):
        """
        Set the last sync time to the variable.
        """
        with self._sync_lock:
            self.__last_sync_time = value
            if value is None:
                self._last_sync_time_var.set(None)
            else:
                self._last_sync_time_var.set(value.timestamp())

    @abstractmethod
    def _fetch_note(self, note_id: Any, *args, **kwargs) -> Optional[Note]:
        """
        Don't call this directly if possible.
        Instead, use :meth:`.get_note` method to retrieve a note and update the cache
        in a thread-safe manner.

        :param note_id: The ID of the note to fetch.
        :return: The latest note from the backend.
        """

    @abstractmethod
    def _fetch_notes(self, *args, **kwargs) -> Iterable[Note]:
        """
        Don't call this directly if possible.
        Instead, use :meth:`.get_notes` method to retrieve notes and update the cache
        in a thread-safe manner.

        :return: The latest list of notes from the backend.
        """

    @abstractmethod
    def _create_note(
        self,
        title: str,
        content: str,
        *args,
        description: Optional[str] = None,
        collection: Optional[Any] = None,
        geo: Optional[Dict[str, Optional[float]]] = None,
        author: Optional[str] = None,
        source: Optional[NoteSource] = None,
        **kwargs,
    ) -> Note:
        """
        Create a new note with the specified title and content.
        """

    @abstractmethod
    def _edit_note(
        self,
        note_id: Any,
        *args,
        title: Optional[str] = None,
        content: Optional[str] = None,
        collection: Optional[Any] = None,
        geo: Optional[Dict[str, Optional[float]]] = None,
        author: Optional[str] = None,
        source: Optional[NoteSource] = None,
        **kwargs,
    ) -> Note:
        """
        Edit an existing note by ID.
        """

    @abstractmethod
    def _delete_note(self, note_id: Any, *args, **kwargs):
        """
        Delete a note by ID.
        """

    @abstractmethod
    def _fetch_collection(
        self, collection_id: Any, *args, **kwargs
    ) -> Optional[NoteCollection]:
        """
        Don't call this directly if possible.
        Instead, use :meth:`.get_collection` to retrieve a collection and update the cache
        in a thread-safe manner.

        :param collection_id: The ID of the collection to fetch.
        :return: The latest collection from the backend.
        """

    @abstractmethod
    def _fetch_collections(self, *args, **kwargs) -> Iterable[NoteCollection]:
        """
        Don't call this directly if possible.
        Instead, use :meth:`.get_collections` to retrieve collections and update the cache
        in a thread-safe manner.

        :return: The latest list of note collections from the backend.
        """

    @abstractmethod
    def _create_collection(
        self,
        title: str,
        *args,
        description: Optional[str] = None,
        parent: Optional[Any] = None,
        **kwargs,
    ) -> NoteCollection:
        """
        Create a new note collection with the specified title and description.
        """

    @abstractmethod
    def _edit_collection(
        self,
        collection_id: Any,
        *args,
        title: Optional[str] = None,
        description: Optional[str] = None,
        parent: Optional[Any] = None,
        **kwargs,
    ) -> NoteCollection:
        """
        Edit an existing note collection by ID.
        """

    @abstractmethod
    def _delete_collection(self, collection_id: Any, *args, **kwargs):
        """
        Delete a note collection by ID.
        This method should be implemented by subclasses.
        """

    def _process_results(  # pylint: disable=too-many-positional-arguments
        self,
        items: Iterable[Any],
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort: Optional[Dict[str, bool]] = None,
        filter: Optional[Dict[str, Any]] = None,  # pylint: disable=redefined-builtin
    ) -> Iterable[Any]:
        if not sort:
            sort = {'created_at': True}

        if filter:
            items = [
                item
                for item in items
                if all(getattr(item, k) == v for k, v in filter.items())
            ]

        items = sorted(
            items,
            key=lambda item: tuple(getattr(item, field) for field in sort.keys()),
            reverse=any(not ascending for ascending in sort.values()),
        )

        if offset is not None:
            items = items[offset:]
        if limit is not None:
            items = items[:limit]

        return items

    def _dispatch_events(self, *events):
        """
        Dispatch the given events to the event bus.
        """
        if not self.bus:
            self.logger.warning(
                'Event bus not available. Events will not be dispatched.'
            )
            return

        for event in events:
            self.bus.post(event)

    def _process_events(
        self,
        notes: Iterable[Note],
        prev_notes: Dict[Any, Note],
        collections: Iterable[NoteCollection],
        prev_collections: Dict[Any, NoteCollection],
    ):
        most_recent_note = list(notes)[0] if notes else None
        most_recent_collection = list(collections)[0] if collections else None
        max_updated_at = max(
            (
                most_recent_note.updated_at.timestamp()
                if most_recent_note and most_recent_note.updated_at
                else 0
            ),
            (
                most_recent_collection.updated_at.timestamp()
                if most_recent_collection and most_recent_collection.updated_at
                else 0
            ),
        )

        with self._sync_lock:
            self._process_collections_events(collections, prev_collections)
            self._process_notes_events(notes, prev_notes)
            self._last_sync_time = (
                datetime.fromtimestamp(max_updated_at) if max_updated_at > 0 else None
            )

    @classmethod
    def _make_event(
        cls, evt_type: Type[BaseNoteEvent], *args, **kwargs
    ) -> BaseNoteEvent:
        """
        Create a note event of the specified type.
        """
        return evt_type(*args, plugin=get_plugin_name_by_class(cls), **kwargs)

    def _process_notes_events(
        self,
        notes: Iterable[Note],
        prev_notes: Dict[Any, Note],
    ):
        last_sync_time = self._last_sync_time.timestamp() if self._last_sync_time else 0
        new_notes_by_id = {note.id: note for note in notes}

        removed_note_events = [
            self._make_event(NoteDeletedEvent, note=note)
            for note_id, note in prev_notes.items()
            if note_id not in new_notes_by_id
        ]

        created_note_events = []
        updated_note_events = []

        for note in notes:
            created_at = note.created_at.timestamp() if note.created_at else 0
            updated_at = note.updated_at.timestamp() if note.updated_at else 0

            if created_at > last_sync_time:
                created_note_events.append(
                    self._make_event(NoteCreatedEvent, note=note)
                )
            elif updated_at > last_sync_time:
                updated_note_events.append(
                    self._make_event(NoteUpdatedEvent, note=note)
                )
            else:
                # Assuming that the list of notes is sorted by updated_at
                break

        self._dispatch_events(
            *removed_note_events,
            *created_note_events,
            *updated_note_events,
        )

    def _process_collections_events(
        self,
        collections: Iterable[NoteCollection],
        prev_collections: Dict[Any, NoteCollection],
    ):
        last_sync_time = self._last_sync_time.timestamp() if self._last_sync_time else 0
        new_collections_by_id = {
            collection.id: collection for collection in collections
        }

        removed_collection_events = [
            self._make_event(CollectionDeletedEvent, collection=collection)
            for collection_id, collection in prev_collections.items()
            if collection_id not in new_collections_by_id
        ]

        created_collection_events = []
        updated_collection_events = []

        for collection in collections:
            created_at = (
                collection.created_at.timestamp() if collection.created_at else 0
            )
            updated_at = (
                collection.updated_at.timestamp() if collection.updated_at else 0
            )

            if created_at > last_sync_time:
                created_collection_events.append(
                    self._make_event(CollectionCreatedEvent, collection=collection)
                )
            elif updated_at > last_sync_time:
                updated_collection_events.append(
                    self._make_event(CollectionUpdatedEvent, collection=collection)
                )
            else:
                # Assuming that the list of collections is sorted by updated_at
                break

        self._dispatch_events(
            *removed_collection_events,
            *created_collection_events,
            *updated_collection_events,
        )

    def _get_note(self, note_id: Any, *args, **kwargs) -> Note:
        note = self._fetch_note(note_id, *args, **kwargs)
        assert note, f'Note with ID {note_id} not found'
        with self._notes_lock:
            # Always overwrite the note in the cache,
            # as this is the most up-to-date complete version
            self._notes[note.id] = note
            if note.parent and note.parent.id in self._collections:
                self._collections[  # pylint: disable=protected-access
                    note.parent.id
                ]._notes[  # pylint: disable=protected-access
                    note.id
                ] = note

        return self._notes[note.id]

    def _get_notes(
        self,
        *args,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort: Optional[Dict[str, bool]] = None,
        filter: Optional[Dict[str, Any]] = None,  # pylint: disable=redefined-builtin
        fetch: bool = False,
        **kwargs,
    ) -> Iterable[Note]:
        # Always fetch if background polling is disabled
        fetch = fetch or not self.poll_interval
        if fetch:
            with self._notes_lock:
                self._notes = {
                    note.id: note for note in self._fetch_notes(*args, **kwargs)
                }
                self._refresh_notes_cache()

        return self._process_results(
            self._notes.values(),
            limit=limit,
            offset=offset,
            sort=sort,
            filter=filter,
        )

    def _get_collection(self, collection_id: Any, *args, **kwargs) -> NoteCollection:
        collection = self._fetch_collection(collection_id, *args, **kwargs)
        assert collection, f'Collection with ID {collection_id} not found'
        with self._collections_lock:
            # Always overwrite the collection in the cache,
            # as this is the most up-to-date complete version
            self._collections[collection.id] = collection
            self._refresh_collections_cache()

        return self._collections[collection.id]

    def _get_collections(
        self,
        *args,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort: Optional[Dict[str, bool]] = None,
        filter: Optional[Dict[str, Any]] = None,  # pylint: disable=redefined-builtin
        fetch: bool = False,
        **kwargs,
    ) -> Iterable[NoteCollection]:
        """
        Get the note collections from the cache or fetch them from the backend if needed.

        :return: An iterable of NoteCollection objects.
        """
        # Always fetch if background polling is disabled
        fetch = fetch or not self.poll_interval
        if fetch:
            with self._collections_lock:
                self._collections = {
                    collection.id: collection
                    for collection in self._fetch_collections(*args, **kwargs)
                }
                self._refresh_collections_cache()

        return self._process_results(
            self._collections.values(),
            limit=limit,
            offset=offset,
            sort=sort,
            filter=filter,
        )

    def _refresh_notes_cache(self):
        for note in list(self._notes.values()):
            if note.parent and note.parent.id in self._collections:
                note.parent = self._collections[note.parent.id]
                self._collections[  # pylint: disable=protected-access
                    note.parent.id
                ]._notes[  # pylint: disable=protected-access
                    note.id
                ] = note

    def _refresh_collections_cache(self):
        for collection in list(self._collections.values()):
            # Link the notes to their parent collections
            for note in list(collection.notes):
                if note.id in self._notes:
                    collection._notes[note.id] = self._notes[
                        note.id
                    ]  # pylint: disable=protected-access

            # Link the child collections to their parent collections
            tmp_collections = list(collection.collections)
            for collection in tmp_collections:
                if collection.id not in self._collections:
                    collection._collections[
                        collection.id
                    ] = self._collections[  # pylint: disable=protected-access
                        collection.id
                    ]

            # Link the parent collections to their child collections
            tmp_collections = list(collection.collections)
            for collection in tmp_collections:
                if collection.parent and collection.parent.id in self._collections:
                    collection.parent = self._collections[collection.parent.id]

    @staticmethod
    def _parse_geo(data: dict) -> Dict[str, Optional[float]]:
        return {
            key: value or None
            for key, value in {
                key: float(data.get(key, 0))
                for key in ('latitude', 'longitude', 'altitude')
            }.items()
        }

    @action
    def get_note(self, note_id: Any, *args, **kwargs) -> dict:
        """
        Get a single note and its full content by ID.

        :param note_id: The ID of the note to retrieve.
        :return: The note as a dictionary, format:

            .. schema:: notes.NoteItemSchema

        """
        return self._get_note(note_id, *args, **kwargs).to_dict()

    @action
    def get_notes(
        self,
        *args,
        limit: Optional[int] = None,
        offset: Optional[int] = 0,
        sort: Optional[Dict[str, bool]] = None,
        filter: Optional[Dict[str, Any]] = None,  # pylint: disable=redefined-builtin
        fetch: bool = False,
        **kwargs,
    ) -> Iterable[dict]:
        """
        Get notes from the cache or fetch them from the backend.

        :param limit: Maximum number of collections to retrieve (default: None, meaning no limit).
        :param offset: Offset to start retrieving collections from (default: 0).
        :param sort: A dictionary specifying the fields to sort by and their order.
            Example: {'created_at': True} sorts by creation date in ascending
            order, while {'created_at': False} sorts in descending order.
        :param filter: A dictionary specifying filters to apply to the collections.
        :param fetch: If True, always fetch the latest collections from the backend,
            regardless of the cache state (default: False).
        :param kwargs: Additional keyword arguments to pass to the fetch method.
        :return: An iterable of notes, format:

            .. schema:: notes.NoteItemSchema(many=True)

        """
        return [
            note.to_dict()
            for note in self._get_notes(
                *args,
                limit=limit,
                offset=offset,
                sort=sort,
                filter=filter,
                fetch=fetch,
                **kwargs,
            )
        ]

    @action
    def create_note(
        self,
        title: str,
        content: str,
        *args,
        description: Optional[str] = None,
        collection: Optional[Any] = None,
        geo: Optional[Dict[str, Optional[float]]] = None,
        source: Optional[dict] = None,
        author: Optional[str] = None,
        **kwargs,
    ) -> dict:
        """
        Create a new note with the specified title and content.

        :param title: The title of the new note.
        :param content: The content of the new note.
        :param description: Optional description for the note.
        :param collection: Optional collection ID to add the note to.
        :param geo: Optional geographical coordinates as a dictionary with the
            fields ``latitude``, ``longitude``, and ``altitude``.
        :param source: Optional source information for the note, with at least
            one of the fields ``url``, ``name`` or ``app``. By default, the
            source is ``platypush`` and the app is ``tech.platypush``.
        :param author: Optional author of the note.
        :return: The created note as a dictionary, format:

            .. schema:: notes.NoteItemSchema
        """
        src = NoteSource(
            **(
                source
                or {
                    'name': 'platypush',
                    'app': 'tech.platypush',
                }
            )
        )

        note = self._create_note(
            title,
            content,
            *args,
            description=description,
            collection=collection,
            geo=self._parse_geo(geo) if geo else None,
            author=author,
            source=src,
            **kwargs,
        )

        with self._notes_lock:
            # Add the new note to the cache
            self._notes[note.id] = note

            # If it has a parent collection, add it to the collection's notes
            if note.parent and note.parent.id in self._collections:
                self._collections[  # pylint: disable=protected-access
                    note.parent.id
                ]._notes[note.id] = note

            # Trigger the note created event
            self._dispatch_events(self._make_event(NoteCreatedEvent, note=note))

        return note.to_dict()

    @action
    def edit_note(
        self,
        note_id: Any,
        *args,
        title: Optional[str] = None,
        content: Optional[str] = None,
        description: Optional[str] = None,
        collection: Optional[Any] = None,
        geo: Optional[Dict[str, Optional[float]]] = None,
        source: Optional[dict] = None,
        author: Optional[str] = None,
        **kwargs,
    ) -> dict:
        """
        Edit an existing note by ID.

        :param note_id: The ID of the note to edit.
        :param title: New title for the note.
        :param content: New content for the note.
        :param description: Optional new description for the note.
        :param collection: New collection ID to move the note under.
        :param geo: Optional geographical coordinates as a dictionary with the
            fields ``latitude``, ``longitude``, and ``altitude``.
        :param source: Optional source information for the note, with at least
            one of the fields ``url``, ``name`` or ``app``.
        :param author: Optional author of the note.
        :return: The updated note as a dictionary, format:

            .. schema:: notes.NoteItemSchema
        """
        with self._notes_lock:
            note = self._edit_note(
                note_id,
                *args,
                title=title,
                content=content,
                description=description,
                collection=collection,
                geo=self._parse_geo(geo) if geo else None,
                author=author,
                source=NoteSource(**source) if source else None,
                **kwargs,
            )

            # Update the cache with the edited note
            self._notes[note.id] = note

            # If it has a parent collection, update it in the collection's notes
            if note.parent and note.parent.id in self._collections:
                self._collections[  # pylint: disable=protected-access
                    note.parent.id
                ]._notes[  # pylint: disable=protected-access
                    note.id
                ] = note

            # Trigger the note updated event
            self._dispatch_events(self._make_event(NoteUpdatedEvent, note=note))

        return note.to_dict()

    @action
    def delete_note(self, note_id: Any, *args, **kwargs):
        """
        Delete a note by ID.

        :param note_id: The ID of the note to delete.
        """
        with self._notes_lock:
            self._delete_note(note_id, *args, **kwargs)
            note = self._notes.pop(note_id, None)
            if not note:
                note = Note(id=note_id, title='')

            # Remove the note from its parent collection if it has one
            if note.parent and note.parent.id in self._collections:
                parent_collection = self._collections[note.parent.id]
                parent_collection.notes.remove(note)

            # Dispatch the deletion event
            self._dispatch_events(self._make_event(NoteDeletedEvent, note=note))

    @action
    def get_collection(self, collection_id: Any, *args, **kwargs) -> dict:
        """
        Get a single note collection by ID.

        :param collection_id: The ID of the collection to retrieve.
        :return: The collection as a dictionary, format:

            .. schema:: notes.NoteCollectionSchema

        """
        return self._get_collection(collection_id, *args, **kwargs).to_dict()

    @action
    def get_collections(
        self,
        *args,
        limit: Optional[int] = None,
        offset: Optional[int] = 0,
        sort: Optional[Dict[str, bool]] = None,
        filter: Optional[Dict[str, Any]] = None,  # pylint: disable=redefined-builtin
        fetch: bool = False,
        **kwargs,
    ) -> Iterable[dict]:
        """
        Get note collections from the cache or fetch them from the backend.

        :param limit: Maximum number of collections to retrieve (default: None, meaning no limit).
        :param offset: Offset to start retrieving collections from (default: 0).
        :param sort: A dictionary specifying the fields to sort by and their order.
            Example: {'created_at': True} sorts by creation date in ascending
            order, while {'created_at': False} sorts in descending order.
        :param filter: A dictionary specifying filters to apply to the collections.
        :param fetch: If True, always fetch the latest collections from the backend,
            regardless of the cache state (default: False).
        :param kwargs: Additional keyword arguments to pass to the fetch method.
        :return: An iterable of note collections, format:

            .. schema:: notes.NoteCollectionSchema(many=True)

        """
        return [
            collection.to_dict()
            for collection in self._get_collections(
                *args,
                limit=limit,
                offset=offset,
                sort=sort,
                filter=filter,
                fetch=fetch,
                **kwargs,
            )
        ]

    @action
    def create_collection(
        self,
        title: str,
        *args,
        description: Optional[str] = None,
        parent: Optional[Any] = None,
        **kwargs,
    ) -> dict:
        """
        Create a new note collection with the specified title and description.

        :param title: The title of the new collection.
        :param description: Optional description for the new collection.
        :param parent: Optional parent collection ID to create a sub-collection.
        :return: The created collection as a dictionary, format:

            .. schema:: notes.NoteCollectionSchema

        """
        collection = self._create_collection(
            title, *args, description=description, parent=parent, **kwargs
        )

        with self._collections_lock:
            # Add the new collection to the cache
            self._collections[collection.id] = collection

            # If it has a parent, add it to the parent's collections
            if collection.parent and collection.parent.id in self._collections:
                parent_collection = self._collections[collection.parent.id]
                parent_collection.collections.append(collection)

            # Trigger the collection created event
            self._dispatch_events(
                self._make_event(CollectionCreatedEvent, collection=collection)
            )

        return collection.to_dict()

    @action
    def edit_collection(
        self,
        collection_id: Any,
        *args,
        title: Optional[str] = None,
        description: Optional[str] = None,
        parent: Optional[Any] = None,
        **kwargs,
    ) -> dict:
        """
        Edit an existing note collection by ID.

        :param collection_id: The ID of the collection to edit.
        :param title: New title for the collection.
        :param description: New description for the collection.
        :param parent: New parent collection ID to move the collection under.
        :return: The updated collection as a dictionary, format:

            .. schema:: notes.NoteCollectionSchema

        """
        with self._collections_lock:
            collection = self._edit_collection(
                collection_id,
                *args,
                title=title,
                description=description,
                parent=parent,
                **kwargs,
            )

            # Update the cache with the edited collection
            old_collection = self._collections.get(collection.id)
            self._collections[collection.id] = collection

            # If the parent has changed, remove it from the old parent's collections
            if (
                old_collection
                and old_collection.parent
                and old_collection.parent != collection.parent
                and old_collection.parent.id in self._collections
            ):
                parent_collection = self._collections.get(old_collection.parent.id)
                if (
                    parent_collection
                    and old_collection in parent_collection.collections
                ):
                    parent_collection.collections.remove(old_collection)

            # If it has a parent, update it in the parent's collections
            if collection.parent and collection.parent.id in self._collections:
                parent_collection = self._collections.get(collection.parent.id)
                if (
                    parent_collection
                    and collection not in parent_collection.collections
                ):
                    parent_collection.collections.append(collection)

            # Trigger the collection updated event
            self._dispatch_events(
                self._make_event(CollectionUpdatedEvent, collection=collection)
            )

        return collection.to_dict()

    @action
    def delete_collection(self, collection_id: Any, *args, **kwargs):
        """
        Delete a note collection by ID.

        :param collection_id: The ID of the collection to delete.
        """
        with self._collections_lock:
            self._delete_collection(collection_id, *args, **kwargs)
            collection = self._collections.pop(collection_id, None)
            if not collection:
                collection = NoteCollection(id=collection_id, title='')

            # Remove the collection from its parent if it has one
            if collection.parent and collection.parent.id in self._collections:
                parent_collection = self._collections[collection.parent.id]
                parent_collection.collections.remove(collection)

            # Dispatch the deletion event
            self._dispatch_events(
                self._make_event(CollectionDeletedEvent, collection=collection)
            )

    @action
    def sync(self, *args, **kwargs):
        """
        Synchronize the notes and collections with the backend.
        This method is called periodically based on the ``poll_interval`` setting.
        If ``poll_interval`` is zero or null, you can manually call this method
        to synchronize the notes and collections.
        """
        t_start = time()
        self.logger.info('Synchronizing notes and collections...')

        with self._sync_lock:
            prev_notes = self._notes.copy()
            prev_collections = self._collections.copy()
            notes = self._get_notes(
                *args, fetch=True, sort={'updated_at': False}, **kwargs
            )
            collections = self._get_collections(
                *args, fetch=True, sort={'updated_at': False}, **kwargs
            )

            self._process_events(
                notes=notes,
                prev_notes=prev_notes,
                collections=collections,
                prev_collections=prev_collections,
            )

        self.logger.info(
            'Synchronization completed in %.2f seconds',
            time() - t_start,
        )

    @action
    def reset_sync(self):
        """
        Reset the last sync time to None, forcing a full resync on the next call to
        :meth:`.sync`, which in turn will re-trigger all notes and collections events.
        """
        self.logger.info('Resetting last sync time')
        with self._sync_lock:
            self._last_sync_time = None
            self._notes.clear()
            self._collections.clear()

    def main(self):
        if not self.poll_interval:
            # If no poll interval is set then we won't poll for new check-ins
            self.wait_stop()
            return

        while not self.should_stop():
            try:
                self.sync()
            except Exception as e:
                self.logger.error('Error during sync: %s', e)
            finally:
                self.wait_stop(self.poll_interval)
