import re
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from threading import RLock
from time import time
from typing import Any, Dict, Iterable, Optional, Type

from platypush.common.notes import Note, NoteCollection, NoteSource
from platypush.context import Variable
from platypush.entities import get_entities_engine
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
from platypush.utils import to_datetime

from .mixins import SyncMixin
from ._model import (
    CollectionsDelta,
    ItemType,
    NotesDelta,
    Results,
    ResultsType,
    StateDelta,
    SyncState,
)


class BaseNotePlugin(  # pylint: disable=too-many-ancestors
    RunnablePlugin, SyncMixin, ABC
):
    """
    Base class for note-taking plugins.
    """

    def __init__(
        self,
        *args,
        poll_interval: float = 300,
        timeout: Optional[int] = 60,
        max_tokens_length: int = 4,
        **kwargs,
    ):
        """
        :param poll_interval: Poll interval in seconds to check for updates (default: 300).
            If set to zero or null, the plugin will not poll for updates,
            and events will be generated only when you manually call :meth:`.sync`.
        :param timeout: Timeout in seconds for the plugin operations (default: 60).
        :param max_tokens_length: If the API used by the plugin doesn't support
            free-text search (that's currently the case for
            :class:`platypush.plugins.nextcloud.notes.NextcloudNotesPlugin` and
            for any notes plugins that use the local file system as a backend),
            then the plugin will use a search index to perform searches. This
            parameter specifies the maximum length of the search tokens that will
            be indexed, where each token is composed of a sequence of
            alphanumeric characters (including underscores). The longer the number,
            the more tokens will be indexed and longer exact phrases will be stored,
            but more disk space will be used for the search index (default: 4).
        """
        RunnablePlugin.__init__(self, *args, poll_interval=poll_interval, **kwargs)
        SyncMixin.__init__(self, *args, max_tokens_length=max_tokens_length, **kwargs)

        self._sync_lock = RLock()
        self._timeout = timeout
        self.__last_sync_time: Optional[datetime] = None

    @property
    def _last_sync_time_var(self) -> Variable:
        """
        Variable name for the last sync time.
        """
        return Variable(f'_LAST_ITEMS_SYNC_TIME[{self._plugin_name}]')

    @property
    def _last_local_sync_time(self) -> Optional[datetime]:
        """
        Get the last sync time from the variable.
        """
        if not self.__last_sync_time:
            t = self._last_sync_time_var.get()
            self.__last_sync_time = datetime.fromtimestamp(float(t)) if t else None

        return self.__last_sync_time

    @_last_local_sync_time.setter
    def _last_local_sync_time(self, value: Optional[datetime]):
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
    def _fetch_notes(
        self,
        *args,
        filter: Optional[Dict[str, Any]] = None,  # pylint: disable=redefined-builtin
        sort: Optional[Dict[str, bool]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        **kwargs,
    ) -> Iterable[Note]:
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
    def _fetch_collections(
        self,
        *args,
        filter: Optional[Dict[str, Any]] = None,  # pylint: disable=redefined-builtin
        sort: Optional[Dict[str, bool]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        **kwargs,
    ) -> Iterable[NoteCollection]:
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
        results_type: ResultsType,
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
                if all(
                    re.search(v, str(getattr(item, k, '')), re.IGNORECASE)
                    for k, v in filter.items()
                )
            ]

        items = sorted(
            items,
            key=lambda item: tuple(getattr(item, field) for field in sort.keys()),
            reverse=any(not ascending for ascending in sort.values()),
        )

        supports_limit = False
        supports_offset = False

        if results_type == ResultsType.NOTES:
            supports_limit = self._api_settings.supports_notes_limit
            supports_offset = self._api_settings.supports_notes_offset
        elif results_type == ResultsType.COLLECTIONS:
            supports_limit = self._api_settings.supports_collections_limit
            supports_offset = self._api_settings.supports_collections_offset
        elif results_type == ResultsType.SEARCH:
            supports_limit = self._api_settings.supports_search_limit
            supports_offset = self._api_settings.supports_search_offset

        if offset is not None and not supports_offset:
            items = items[offset:]
        if limit is not None and not supports_limit:
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

    def _process_events(self, state_delta: StateDelta):
        with self._sync_lock:
            self._process_collections_events(state_delta.collections)
            self._process_notes_events(state_delta.notes)

    def _make_event(
        self, evt_type: Type[BaseNoteEvent], *args, **kwargs
    ) -> BaseNoteEvent:
        """
        Create a note event of the specified type.
        """
        return evt_type(*args, plugin=self._plugin_name, **kwargs)

    def _process_notes_events(self, notes_delta: NotesDelta):
        removed_note_events = [
            self._make_event(NoteDeletedEvent, note=note)
            for note in notes_delta.deleted.values()
        ]

        created_note_events = [
            self._make_event(NoteCreatedEvent, note=note)
            for note in notes_delta.added.values()
        ]

        updated_note_events = [
            self._make_event(NoteUpdatedEvent, note=note)
            for note in notes_delta.updated.values()
        ]

        self._dispatch_events(
            *removed_note_events,
            *created_note_events,
            *updated_note_events,
        )

    def _process_collections_events(self, collections_delta: CollectionsDelta):
        removed_collection_events = [
            self._make_event(CollectionDeletedEvent, collection=collection)
            for collection in collections_delta.deleted.values()
        ]

        created_collection_events = [
            self._make_event(CollectionCreatedEvent, collection=collection)
            for collection in collections_delta.added.values()
        ]

        updated_collection_events = [
            self._make_event(CollectionUpdatedEvent, collection=collection)
            for collection in collections_delta.updated.values()
        ]

        self._dispatch_events(
            *removed_collection_events,
            *created_collection_events,
            *updated_collection_events,
        )

    def _get_note(self, note_id: Any, *args, **kwargs) -> Note:
        note = self._fetch_note(note_id, *args, **kwargs)
        assert note, f'Note with ID {note_id} not found'
        with self._sync_lock:
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

    def _merge_note(self, note: Note, skip_content: bool = True) -> Note:
        """
        Merge the state of an incoming note with the existing one in the cache.
        """

        existing_note = self._notes.get(note.id)
        if not existing_note:
            # If the note doesn't exist, just return the new one
            return note

        for field in note.__dataclass_fields__:
            existing_value = getattr(existing_note, field)
            value = getattr(note, field)
            # Don't overwrite content, digest and tags here unless they have been re-fetched
            if (
                skip_content
                and field in ('content', 'digest', 'tags')
                and existing_value
                and not value
            ):
                continue

            setattr(existing_note, field, value)

        return existing_note

    def _merge_remote_note_relations(
        self,
        new_notes: Dict[Any, Note],
        existing_notes: Dict[Any, Note],
    ) -> Dict[Any, Note]:
        """
        This merges the relations of the notes upon initial sync, to ensure
        that any existing relationships are not lost when fetched again from
        the remote API.

        :param new_notes: The new notes fetched from the remote API.
        :param existing_notes: The existing notes in the local cache.
        :return: The updated notes with merged relations.
        """
        for note in new_notes.values():
            existing_note = existing_notes.get(note.id)
            if not existing_note:
                continue

            # Merge synced_from/synced_to/conflict_note relations
            note.synced_from = existing_note.synced_from or note.synced_from
            note.synced_to = existing_note.synced_to or note.synced_to
            note.conflict_notes = existing_note.conflict_notes or note.conflict_notes

        return new_notes

    def _deduplicate_notes(self, notes: Iterable[Note]) -> Dict[Any, Note]:
        """
        Deduplicate notes based on their path, keeping the most recently updated one.
        """
        deduped_notes = {}
        for note in notes:
            if note.path not in deduped_notes or (
                note.updated_at
                and (
                    not deduped_notes[note.path].updated_at
                    or note.updated_at > deduped_notes[note.path].updated_at
                )
            ):
                deduped_notes[note.path] = note

        return {note.id: note for note in deduped_notes.values()}

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
            with self._sync_lock:
                cached_notes = self._notes.copy()
                new_notes = {
                    note.id: self._merge_note(note)
                    for note in self._fetch_notes(
                        *args,
                        limit=limit,
                        offset=offset,
                        sort=sort,
                        filter=filter,
                        **kwargs,
                    )
                }

                self._notes = self._deduplicate_notes(
                    self._merge_remote_note_relations(
                        new_notes=new_notes, existing_notes=cached_notes
                    ).values()
                )

                self._refresh_notes_cache()

        return self._process_results(
            self._notes.values(),
            limit=limit,
            offset=offset,
            sort=sort,
            filter=filter,
            results_type=ResultsType.NOTES,
        )

    def _get_collection(self, collection_id: Any, *args, **kwargs) -> NoteCollection:
        collection = self._fetch_collection(collection_id, *args, **kwargs)
        assert collection, f'Collection with ID {collection_id} not found'
        with self._sync_lock:
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
            with self._sync_lock:
                self._collections = {
                    collection.id: collection
                    for collection in self._fetch_collections(
                        *args,
                        limit=limit,
                        offset=offset,
                        sort=sort,
                        filter=filter,
                        **kwargs,
                    )
                }
                self._refresh_collections_cache()

        return self._process_results(
            self._collections.values(),
            limit=limit,
            offset=offset,
            sort=sort,
            filter=filter,
            results_type=ResultsType.COLLECTIONS,
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
                    # pylint: disable=protected-access
                    collection._notes[note.id] = self._notes[note.id]

            # Link the child collections to their parent collections
            tmp_collections = list(collection.collections)
            for collection in tmp_collections:
                if collection.id not in self._collections:
                    # pylint: disable=protected-access
                    collection._collections[collection.id] = self._collections[
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

    def _get_state_delta(
        self,
        *,
        previous_notes: Dict[Any, Note],
        previous_collections: Dict[Any, NoteCollection],
        notes: Dict[Any, Note],
        collections: Dict[Any, NoteCollection],
        filter_by_latest_updated_at: bool = True,
        **_,
    ) -> StateDelta:
        """
        Get the state delta between the previous and current state of notes and collections.

        :param previous_notes: Previous notes state.
        :param previous_collections: Previous collections state.
        :param notes: Current notes state.
        :param collections: Current collections state.
        :param filter_by_latest_updated_at: If True, select only the changes
            more recent than the latest updated_at timestamp.
        :return: A StateDelta object containing the changes.
        """
        state_delta = StateDelta()
        latest_updated_at = new_latest_updated_at = (
            self._last_local_sync_time.timestamp() if self._last_local_sync_time else 0
        )

        # Get new and updated notes
        for note in notes.values():
            updated_at = note.updated_at.timestamp() if note.updated_at else 0
            if not filter_by_latest_updated_at or updated_at > latest_updated_at:
                if note.id not in previous_notes:
                    state_delta.notes.added[note.id] = note
                else:
                    state_delta.notes.updated[note.id] = note

            new_latest_updated_at = max(new_latest_updated_at, updated_at)

        # Get deleted notes
        for note_id in previous_notes:
            if note_id not in notes:
                state_delta.notes.deleted[note_id] = previous_notes[note_id]

        collections = {
            **{note.parent.id: note.parent for note in notes.values() if note.parent},
            **collections,
        }

        # Get new and updated collections
        for collection in collections.values():
            updated_at = (
                collection.updated_at.timestamp() if collection.updated_at else 0
            )
            if not filter_by_latest_updated_at or updated_at > latest_updated_at:
                if collection.id not in previous_collections:
                    state_delta.collections.added[collection.id] = collection
                else:
                    state_delta.collections.updated[collection.id] = collection

            new_latest_updated_at = max(new_latest_updated_at, updated_at)

        # Get deleted collections
        for collection_id in previous_collections:
            if collection_id not in collections:
                state_delta.collections.deleted[collection_id] = previous_collections[
                    collection_id
                ]

        state_delta.latest_updated_at = new_latest_updated_at
        return state_delta

    def _refresh_notes(self, notes: Dict[Any, Note]):
        """
        Fetch the given notes from the backend and update the cache.
        """
        if not notes:
            return

        self.logger.info(
            'Refreshing the state for %d notes from the backend', len(notes)
        )

        with ThreadPoolExecutor(max_workers=5) as pool:
            # Fetch notes in parallel
            futures = [
                pool.submit(self._fetch_note, note.id) for note in notes.values()
            ]

            # Wait for all futures to complete and collect the results
            results = pool.map(lambda f: f.result(), futures)

        with self._sync_lock:
            self._notes.update(
                {note.id: self._merge_note(note) for note in results if note}
            )
            self._refresh_notes_cache()

    @abstractmethod
    def _search(
        self,
        query: str,
        *args,
        item_type: ItemType,
        include_terms: Optional[Dict[str, Any]] = None,
        exclude_terms: Optional[Dict[str, Any]] = None,
        created_before: Optional[datetime] = None,
        created_after: Optional[datetime] = None,
        updated_before: Optional[datetime] = None,
        updated_after: Optional[datetime] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = 0,
        **kwargs,
    ) -> Results:
        """
        Search for notes or collections based on the provided query and filters.
        """

    @action
    def search(
        self,
        *args,
        query: str,
        type: str = ItemType.NOTE.value,  # pylint: disable=redefined-builtin
        include_terms: Optional[Dict[str, Any]] = None,
        exclude_terms: Optional[Dict[str, Any]] = None,
        created_before: Optional[datetime] = None,
        created_after: Optional[datetime] = None,
        updated_before: Optional[datetime] = None,
        updated_after: Optional[datetime] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = 0,
        **kwargs,
    ):
        """
        Search for notes or collections based on the provided query and filters.

        In most of the cases (but it depends on the backend) double-quoted
        search terms will match exact phrases, while unquoted queries will
        match any of the words in the query.

        Wildcards (again, depending on the backend) in the search terms are
        also supported.

        :param query: The search query string (it will be searched in all the
            fields).
        :param type: The type of items to search for - ``note``,
            ``collection``, or ``tag`` (default: ``note``).
        :param include_terms: Optional dictionary of terms to include in the search.
            The keys are field names and the values are strings to match against.
        :param exclude_terms: Optional dictionary of terms to exclude from the search.
            The keys are field names and the values are strings to exclude from the results.
        :param created_before: Optional datetime ISO string or UNIX timestamp
            to filter items created before this date.
        :param created_after: Optional datetime ISO string or UNIX timestamp
            to filter items created after this date.
        :param updated_before: Optional datetime ISO string or UNIX timestamp
            to filter items updated before this date.
        :param updated_after: Optional datetime ISO string or UNIX timestamp
            to filter items updated after this date.
        :param limit: Maximum number of items to retrieve (default: None,
            meaning no limit, or depending on the default limit of the backend).
        :param offset: Offset to start retrieving items from (default: 0).
        :return: An iterable of matching items, format:

            .. code-block:: javascript

                {
                    "has_more": false
                    "results" [
                        {
                            "type": "note",
                            "item": {
                                "id": "note-id",
                                "title": "Note Title",
                                "content": "Note content...",
                                "created_at": "2023-10-01T12:00:00Z",
                                "updated_at": "2023-10-01T12:00:00Z",
                                // ...
                            }
                        }
                    ]
                }

        """
        method = self._search if self._api_settings.supports_search else self._db_search

        return method(
            query,
            *args,
            item_type=ItemType(type),
            include_terms=include_terms,
            exclude_terms=exclude_terms,
            created_before=to_datetime(created_before) if created_before else None,
            created_after=to_datetime(created_after) if created_after else None,
            updated_before=to_datetime(updated_before) if updated_before else None,
            updated_after=to_datetime(updated_after) if updated_after else None,
            limit=limit,
            offset=offset,
            **kwargs,
        ).to_dict()

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
        :param filter: A dictionary specifying filters to apply to the notes, in the form
            of a dictionary where the keys are field names and the values are regular expressions
            to match against the field values.
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

        with self._sync_lock:
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

        with self._sync_lock:
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
        self._delete_note(note_id, *args, **kwargs)

        with self._sync_lock:
            note = self._notes.pop(note_id, None)
            if not note:
                note = Note(id=note_id, plugin=self._plugin_name, title='')

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
        :param filter: A dictionary specifying filters to apply to the collections, in the form
            of a dictionary where the keys are field names and the values are regular expressions
            to match against the field values.
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

        with self._sync_lock:
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
        collection = self._edit_collection(
            collection_id,
            *args,
            title=title,
            description=description,
            parent=parent,
            **kwargs,
        )

        with self._sync_lock:
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
        self._delete_collection(collection_id, *args, **kwargs)

        with self._sync_lock:
            collection = self._collections.pop(collection_id, None)
            if not collection:
                collection = NoteCollection(
                    id=collection_id, plugin=self._plugin_name, title=''
                )

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
        self.sync_state = SyncState.SYNCING_LOCAL

        # Wait for the entities engine to start
        get_entities_engine().wait_start()

        t_start = time()
        self.logger.info('Synchronizing notes and collections...')

        with self._sync_lock:
            # Initialize the latest state from the database if not already done
            self._db_init()
            prev_notes = self._notes.copy()
            prev_collections = self._collections.copy()

            # Fetch the latest version of the notes from the backend
            notes = {
                note.id: note
                for note in self._get_notes(
                    *args, fetch=True, sort={'updated_at': False}, **kwargs
                )
            }

            # Fetch the latest version of the collections from the backend
            collections = {
                collection.id: collection
                for collection in self._get_collections(
                    *args, fetch=True, sort={'updated_at': False}, **kwargs
                )
            }

            # Get the state delta between the previous and current state
            state_delta = self._get_state_delta(
                previous_notes=prev_notes,
                previous_collections=prev_collections,
                notes=notes,
                collections=collections,
            )

            # Re-fetch any notes that have been updated since the last sync
            self._refresh_notes(
                {**state_delta.notes.added, **state_delta.notes.updated}
            )

            # Update the local cache with the latest notes and collections
            if not state_delta.is_empty():
                self.logger.info('Synchronizing changes: %s', state_delta)

            try:
                self._db_sync(state_delta)
            except Exception as e:
                self.logger.error(
                    'Error during local sync: %s',
                    e,
                )
                raise e

            self._last_local_sync_time = datetime.fromtimestamp(
                state_delta.latest_updated_at
            )
            self.sync_state = SyncState.SYNCED_LOCAL

        self._process_events(state_delta)
        self.logger.info(
            'Local synchronization completed in %.2f seconds',
            time() - t_start,
        )

        # Initialize remote sync if not already done
        self.start_remote_sync()

    @action
    def reset_sync(self):
        """
        Reset the sync state.

            1. Reset the last sync time to None, forcing a full resync on the
               next call to :meth:`.sync`, which in turn will re-trigger all
               notes and collections events.
            2. Clear the local notes and collections cache.
        """
        self.logger.info('Resetting last sync time')
        with self._sync_lock:
            self._db_clear()
            self._last_local_sync_time = None
            self._notes.clear()
            self._collections.clear()
            self.sync_state = SyncState.UNINITIALIZED

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
