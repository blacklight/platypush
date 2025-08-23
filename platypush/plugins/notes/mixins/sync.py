import datetime
from abc import ABC, abstractmethod
from collections import defaultdict
from logging import Logger
from threading import Event, RLock
from time import time
from typing import Callable, Dict, List, Optional, Union, Any

from dateutil import tz

from platypush.common.notes import Note, NoteCollection, Storable
from platypush.context import Variable, get_bus
from platypush.message import Message
from platypush.message.event.notes import BaseNoteEvent
from platypush.message.response import Response
from platypush.plugins import PluginRegistry, action
from platypush.plugins.notes._model import StateDelta
from platypush.utils import get_plugin_name_by_class

from .._model import SyncConfig, SyncConflictResolution, SyncState
from .db import DbMixin


class LastSyncVars(dict[str, Variable]):
    """
    Proxy class for storing the last synchronization variables.
    """

    _VARNAME_TEMPLATE = "_LAST_REMOTE_ITEMS_SYNC_TIME[{plugin}][{remote}]"

    def __init__(self, plugin: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plugin = plugin

    def __missing__(self, key: str) -> Variable:
        """
        Return a new Variable instance if the key is missing.

        :param key: The key to look up in the dictionary.
        :return: A new Variable instance with the given key.
        """
        self[key] = Variable(
            self._VARNAME_TEMPLATE.format(plugin=self.plugin, remote=key)
        )
        return self[key]

    def get_time(self, key: str) -> float:
        """
        Get the timestamp value for the given key.

        :param key: The key to look up in the dictionary.
        :return: The value for the given key, as a float timestamp, or 0.
        """
        value = self[key].get()  # type: ignore
        if not value:
            return 0

        try:
            return float(value)
        except (TypeError, ValueError):
            return 0

    def set_time(
        self,
        key: str,
        value: Optional[Union[int, float, str, datetime.datetime]] = None,
    ):
        """
        Set the timestamp value for the given key.

        :param key: The key to set in the dictionary.
        :param value: The value to set, which can be an int, float, str, or
            datetime. If none is passed, the current time will be used.
        """
        if not value:
            value = time()
        if isinstance(value, datetime.datetime):
            value = value.timestamp()
        elif isinstance(value, str):
            try:
                value = float(value)
            except ValueError:
                try:
                    value = datetime.datetime.fromisoformat(value).timestamp()
                except ValueError:
                    self[key].set(None)
                    return

        self[key].set(value)  # type: ignore


class SyncMixin(DbMixin, ABC):
    """
    Handles the synchronization of data between different note stores.
    """

    logger: Logger

    def __init__(
        self, *args, sync_from: Optional[List[Union[dict, SyncConfig]]] = None, **kwargs
    ):
        """
        Initialize the SyncMixin with synchronization settings.

        :param sync_from: A list of dictionaries or SyncConfig instances
            specifying the plugins to sync from.
        """
        super().__init__(*args, **kwargs)
        self.sync_from: List[SyncConfig] = []
        self._sync_state = SyncState.UNINITIALIZED
        self._sync_state_lock = RLock()
        self._sync_events: Dict[SyncState, Event] = defaultdict(Event)
        self._unregister_sync_handlers: List[Callable[[], None]] = []
        self._last_sync_vars = LastSyncVars(plugin=self._plugin_name)
        self.sync_state = SyncState.UNINITIALIZED

        if not sync_from:
            return

        for item in sync_from:
            assert isinstance(
                item, (dict, SyncConfig)
            ), "sync_from must be a list of dictionaries or SyncConfig instances."
            if isinstance(item, dict):
                self.sync_from.append(SyncConfig(**item))
            elif isinstance(item, SyncConfig):
                self.sync_from.append(item)

    @property
    def sync_state(self) -> SyncState:
        """
        Get the current synchronization state.

        :return: The current synchronization state.
        """
        with self._sync_state_lock:
            return self._sync_state

    @sync_state.setter
    def sync_state(self, state: SyncState):  # pylint:disable=too-many-branches
        """
        Set the current synchronization state and notify any waiting threads.

        :param state: The new synchronization state.
        """
        with self._sync_state_lock:
            if self._sync_state == state:
                return

            self.logger.debug('Setting sync state to %s', state)
            self._sync_state = state
            self._sync_events[state].set()

            if state == SyncState.UNINITIALIZED:
                for s in SyncState:
                    if s != SyncState.UNINITIALIZED:
                        self._sync_events[s].clear()
            elif state == SyncState.SYNCING_LOCAL:
                for s in [
                    SyncState.UNINITIALIZED,
                    SyncState.SYNCED_LOCAL,
                    SyncState.READY,
                ]:
                    self._sync_events[s].clear()
            elif state == SyncState.SYNCED_LOCAL:
                for s in [SyncState.UNINITIALIZED, SyncState.SYNCING_LOCAL]:
                    self._sync_events[s].clear()
                if self._sync_events[SyncState.SYNCED_REMOTE].is_set():
                    self._sync_events[SyncState.READY].set()
                    self._sync_state = SyncState.READY
            elif state == SyncState.SYNCING_REMOTE:
                for s in [
                    SyncState.UNINITIALIZED,
                    SyncState.SYNCED_REMOTE,
                    SyncState.READY,
                ]:
                    self._sync_events[s].clear()
            elif state == SyncState.SYNCED_REMOTE:
                for s in [SyncState.UNINITIALIZED, SyncState.SYNCING_REMOTE]:
                    self._sync_events[s].clear()
                if self._sync_events[SyncState.SYNCED_LOCAL].is_set():
                    self._sync_events[SyncState.READY].set()
                    self._sync_state = SyncState.READY
            elif state == SyncState.READY:
                for s in [
                    SyncState.UNINITIALIZED,
                    SyncState.SYNCING_LOCAL,
                    SyncState.SYNCING_REMOTE,
                ]:
                    self._sync_events[s].clear()

    def wait_sync_state(self, state: SyncState, timeout: Optional[float] = None):
        """
        Wait for the synchronization state to change to the specified state.

        :param state: The synchronization state to wait for.
        :param timeout: Optional timeout in seconds. If None, wait indefinitely.
        :raise TimeoutError: If the timeout is reached before the state changes.
        """
        with self._sync_state_lock:
            if self._sync_state == state:
                return

        if not self._sync_events[state].wait(timeout=timeout):
            raise TimeoutError(
                f'Timed out waiting for sync state {state.name} after {timeout} seconds.'
            )

    def _event_handler(self, event: Message):
        """
        Handle incoming events related to note synchronization.

        :param event: The event to handle.
        """
        if self._sync_state != SyncState.READY:
            self.logger.debug('Sync state is not READY, ignoring event: %s', event)
            return

        self.logger.debug('Handling event: %s', event)
        # TODO Handle events for real-time synchronization

    def _get_sync_dependencies(self):
        from platypush.plugins.notes import BaseNotePlugin

        # First, make sure that the plugin doesn't depend on itself
        if any(
            sync_config.plugin == self._plugin_name for sync_config in self.sync_from
        ):
            raise ValueError(
                f'Plugin {self._plugin_name} cannot synchronize with itself.'
            )

        notes_plugins: Dict[str, BaseNotePlugin] = {  # type:ignore
            get_plugin_name_by_class(plugin): plugin
            for plugin in PluginRegistry.get_plugins_by_type(BaseNotePlugin)
        }

        dependencies: List[BaseNotePlugin] = [
            plugin
            for _, plugin in sorted(
                {
                    config.plugin: notes_plugins[config.plugin]
                    for config in self.sync_from
                    if config.plugin in notes_plugins
                }.items(),
                key=lambda item: item[0],
            )
        ]

        return dependencies

    def _remote_sync(self):
        """
        Initialize the remote synchronization state.
        """
        t_start_all = time()

        with self._sync_lock:
            self.sync_state = SyncState.SYNCING_REMOTE
            deps = {
                get_plugin_name_by_class(plugin.__class__): plugin
                for plugin in self._get_sync_dependencies()
            }

            sync_configs = {
                config.plugin: config
                for config in self.sync_from
                if config.plugin in deps
            }

            for plugin_name, plugin in deps.items():
                sync_config = sync_configs.get(plugin_name)
                if not (sync_config and sync_config.pull_remote):
                    # If mirroring is disabled, we skip the initial sync
                    continue

                self.logger.debug(
                    'Waiting for initial sync from plugin %s', sync_config.plugin
                )

                t_start = time()
                plugin.wait_sync_state(
                    SyncState.SYNCED_LOCAL, timeout=sync_config.timeout
                )
                notes = list(
                    plugin._get_notes(  # pylint:disable=protected-access
                        limit=99999, offset=0
                    )
                )

                self._process_remote_items(notes=notes, sync_config=sync_config)
                self.logger.info(
                    'Initial sync from plugin %s completed in %.2f seconds',
                    plugin_name,
                    time() - t_start,
                )

            self.sync_state = SyncState.SYNCED_REMOTE

        self.logger.info(
            'All initial remote syncs completed in %.2f seconds',
            time() - t_start_all,
        )

    def _process_remote_items(self, notes: List[Note], sync_config: SyncConfig):
        """
        Handle the remote items fetched from the synchronization source.

        :param notes: List of remote notes to handle.
        :param sync_config: The synchronization configuration for the source.
        """

        if not notes:
            self.logger.debug(
                'No notes or collections to handle for plugin %s', sync_config.plugin
            )
            return

        state_delta = self._get_remote_state_delta(
            notes={note.id: note for note in notes},
            sync_config=sync_config,
        )

        if state_delta.is_empty():
            return

        self.logger.info(
            'Synchronizing changes from plugin %s: %s',
            sync_config.plugin,
            state_delta,
        )

        self._persist_remote_state_delta(
            state_delta=state_delta, sync_config=sync_config
        )

        self._last_sync_vars.set_time(sync_config.plugin)

    def _persist_remote_state_delta(
        self, state_delta: StateDelta, *, sync_config: SyncConfig
    ):
        """
        Persist the state delta from the remote source to the plugin and to the
        local database.

        :param state_delta: The state delta to persist.
        :param sync_config: The synchronization configuration for the source.
        """

        def _execute_action(func: Callable[..., Response], *args, **kwargs):
            errors = []
            try:
                result = func(*args, **kwargs)
                if result.errors:
                    errors = result.errors
                else:
                    return result.output
            except Exception as e:
                errors = [str(e)]

            if errors:
                self.logger.error(
                    'Failed to execute action %s with errors: %s',
                    func.__name__,
                    ', '.join(errors),
                )

            return {}

        with self._sync_lock:
            # Handle new collections
            for collection in state_delta.collections.added.values():
                self.logger.debug(
                    'Adding collection %s from plugin %s',
                    collection.id,
                    sync_config.plugin,
                )

                _execute_action(
                    self.create_collection,
                    **{
                        **collection.to_dict(),
                        'parent': (
                            self._infer_id(collection.parent)
                            if collection.parent
                            else None
                        ),
                    },
                )

            # Handle updated collections
            for collection in state_delta.collections.updated.values():
                self.logger.debug(
                    'Updating collection %s from plugin %s',
                    collection.id,
                    sync_config.plugin,
                )

                _execute_action(
                    self.edit_collection,
                    collection_id=collection.id,
                    **{
                        **collection.to_dict(),
                        'parent': (
                            self._infer_id(collection.parent)
                            if collection.parent
                            else None
                        ),
                    },
                )

            # Handle new notes
            for note in state_delta.notes.added.values():
                self.logger.debug(
                    'Adding note %s from plugin %s', note.id, sync_config.plugin
                )

                _execute_action(
                    self.create_note,
                    **{
                        **note.to_dict(minimal=True),
                        'content': note.content or '',
                        'parent': (
                            self._infer_id(note.parent) if note.parent else None
                        ),
                    },
                )

            # Handle updated notes
            for note in state_delta.notes.updated.values():
                self.logger.debug(
                    'Updating note %s from plugin %s', note.id, sync_config.plugin
                )

                _execute_action(
                    self.edit_note,
                    note_id=note.id,
                    **{
                        **note.to_dict(minimal=True),
                        'content': note.content or '',
                        'parent': (
                            self._infer_id(note.parent) if note.parent else None
                        ),
                    },
                )

            # Handle deleted notes
            for note in state_delta.notes.deleted.values():
                self.logger.debug(
                    'Deleting note %s from plugin %s', note.id, sync_config.plugin
                )
                _execute_action(self.delete_note, note_id=note.id)

            # Save changes to the database
            self._db_sync(state_delta)

    def _merge_notes(
        self,
        local_note: Note,
        remote_note: Note,
        *,
        sync_config: SyncConfig,
        state_delta: StateDelta,
    ):
        """
        Merge notes and handle conflicts between local and remote notes.

        :param local_note: The local note. Its content will be updated with the
            remote note's content if required.
        :param remote_note: The remote note.
        :param sync_config: The synchronization configuration.
        :param state_delta: The state delta to update with any changes.
        """
        existing_conflict_notes_by_remote_id = {
            remote_note.id: self._notes[conflict_note.id]
            for conflict_note in (local_note.conflict_notes or [])
            if conflict_note.id in self._notes
        }

        existing_conflict_note = existing_conflict_notes_by_remote_id.get(
            remote_note.id
        )
        conflict_note = None
        remote_note_updated_at = self._normalize_datetime(remote_note.updated_at)
        local_note_updated_at = self._normalize_datetime(local_note.updated_at)

        # No conflict, the notes are identical
        if local_note.digest == remote_note.digest:
            local_note.conflict_notes = list(
                {
                    note.id: note
                    for note in (local_note.conflict_notes or [])
                    if note.id != remote_note.id
                }.values()
            )

        # If the remote version is newer, or the integration is configured in
        # overwrite mode, update the local note
        elif (
            remote_note_updated_at
            and (
                not local_note_updated_at
                or remote_note_updated_at > local_note_updated_at
            )
            or sync_config.conflict_resolution == SyncConflictResolution.OVERWRITE
        ):
            self.logger.debug(
                'Overwriting local note %s with remote note %s',
                local_note.id,
                remote_note.id,
            )
            local_note.content = remote_note.content
            local_note.content_type = remote_note.content_type
            local_note.title = remote_note.title
            local_note.description = remote_note.description
            local_note.digest = remote_note.digest
            local_note.tags = remote_note.tags
            local_note.latitude = remote_note.latitude
            local_note.longitude = remote_note.longitude
            local_note.altitude = remote_note.altitude
            local_note.author = remote_note.author
            local_note.source = remote_note.source
            local_note.parent = (
                self._convert_remote_collection_to_local(remote_note.parent)
                if remote_note.parent
                else None
            )
            local_note.conflict_notes = list(
                {
                    note.id: note
                    for note in (local_note.conflict_notes or [])
                    if note.id != remote_note.id
                }.values()
            )
            local_note.updated_at = datetime.datetime.now()

        # Ignore the conflict and do not update the local note
        elif sync_config.conflict_resolution == SyncConflictResolution.IGNORE:
            self.logger.debug(
                'Ignoring conflict for note %s between local and remote versions.',
                local_note.id,
            )
            local_note.conflict_notes = list(
                {
                    note.id: note
                    for note in (local_note.conflict_notes or [])
                    if note.id != remote_note.id
                }.values()
            )

        # Create or update the conflict note
        else:
            if existing_conflict_note:
                self.logger.debug(
                    'Merging conflict note %s with remote note %s',
                    existing_conflict_note.id,
                    remote_note.id,
                )
                existing_conflict_note.content = remote_note.content
                existing_conflict_note.content_type = remote_note.content_type
                existing_conflict_note.description = remote_note.description
                existing_conflict_note.digest = remote_note.digest
                existing_conflict_note.tags = remote_note.tags
                existing_conflict_note.latitude = remote_note.latitude
                existing_conflict_note.longitude = remote_note.longitude
                existing_conflict_note.altitude = remote_note.altitude
                existing_conflict_note.author = remote_note.author
                existing_conflict_note.source = remote_note.source
                existing_conflict_note.updated_at = datetime.datetime.now()
                conflict_note = existing_conflict_note
                state_delta.notes.updated[
                    existing_conflict_note.id
                ] = existing_conflict_note
            else:
                conflict_note = Note(
                    id=remote_note.id,
                    title=f'__CONFLICT__[{remote_note.plugin}]{remote_note.title}',
                    plugin=self._plugin_name,
                    content=remote_note.content,
                    content_type=remote_note.content_type,
                    parent=local_note.parent,
                    tags=remote_note.tags,
                    digest=remote_note.digest,
                    latitude=remote_note.latitude,
                    longitude=remote_note.longitude,
                    altitude=remote_note.altitude,
                    author=remote_note.author,
                    source=remote_note.source,
                    created_at=datetime.datetime.now(),
                    updated_at=datetime.datetime.now(),
                )

                conflict_note.id = self._infer_id(conflict_note)
                local_note.conflict_notes = list(
                    {
                        **{note.id: note for note in (local_note.conflict_notes or [])},
                        conflict_note.id: conflict_note,
                    }.values()
                )

                state_delta.notes.added[conflict_note.id] = conflict_note
                self.logger.warning(
                    'Conflict detected for note %s between local and remote versions. Creating conflict note %s.',
                    local_note.path,
                    conflict_note.path,
                )

        # Mark the conflict note for deletion if the conflict has been solved
        if existing_conflict_note and not conflict_note:
            self.logger.info(
                'Conflict for note %s has been resolved. Deleting conflict note %s.',
                local_note.path,
                existing_conflict_note.path,
            )

            state_delta.notes.deleted[
                existing_conflict_note.id
            ] = existing_conflict_note

    def _convert_remote_note_to_local(
        self, remote_note: Note, *, sync_config: SyncConfig, state_delta: StateDelta
    ) -> Note:
        """
        Convert a remote note to a local synced one.

        :param remote_note: The remote note to convert.
        :param sync_config: The synchronization configuration.
        :param state_delta: The state delta to update with any changes.
        """
        existing_local_note = self._notes_by_path.get(remote_note.path)
        if not existing_local_note:
            local_note = Note(
                id=self._infer_id(remote_note),
                title=remote_note.title,
                plugin=self._plugin_name,
                content=remote_note.content,
                content_type=remote_note.content_type,
                parent=(
                    self._convert_remote_collection_to_local(remote_note.parent)
                    if remote_note.parent
                    else None
                ),
                tags=remote_note.tags,
                digest=remote_note.digest,
                latitude=remote_note.latitude,
                longitude=remote_note.longitude,
                altitude=remote_note.altitude,
                author=remote_note.author,
                source=remote_note.source,
                created_at=remote_note.created_at,
                updated_at=remote_note.updated_at,
            )
        else:
            local_note = existing_local_note
            self._merge_notes(
                local_note=local_note,
                remote_note=remote_note,
                sync_config=sync_config,
                state_delta=state_delta,
            )

        local_note.synced_from = list(
            {
                **{
                    # pylint:disable=protected-access
                    note._db_id: note
                    for note in local_note.synced_from
                },
                remote_note._db_id: remote_note,  # pylint:disable=protected-access
            }.values()
        )

        remote_note.synced_to = list(
            {
                **{
                    # pylint:disable=protected-access
                    note._db_id: note
                    for note in remote_note.synced_to
                },
                local_note._db_id: local_note,  # pylint:disable=protected-access
            }.values()
        )

        if not existing_local_note:
            local_note.created_at = datetime.datetime.now()
            local_note.updated_at = datetime.datetime.now()

        local_note.id = self._infer_id(local_note)
        return local_note

    def _convert_remote_collection_to_local(
        self, remote_collection: NoteCollection
    ) -> NoteCollection:
        """
        Convert a remote collection to a local synced one.
        """
        existing_local_collection = self._collections_by_path.get(
            remote_collection.path
        )

        if not existing_local_collection:
            return NoteCollection(
                id=self._infer_id(remote_collection),
                title=remote_collection.title,
                plugin=self._plugin_name,
                parent=(
                    self._convert_remote_collection_to_local(remote_collection.parent)
                    if remote_collection.parent
                    else None
                ),
                created_at=remote_collection.created_at,
                updated_at=remote_collection.updated_at,
            )

        return existing_local_collection

    def _get_remote_state_delta(
        self,
        notes: Dict[Any, Note],
        *,
        sync_config: SyncConfig,
        **_: Any,
    ) -> StateDelta:
        state_delta = StateDelta()

        # Handle new and updated notes
        state_delta = self._calculate_added_and_updated_notes(
            notes=notes, sync_config=sync_config, state_delta=state_delta
        )

        # Handle deleted notes
        state_delta = self._calculate_deleted_notes(
            notes=notes, sync_config=sync_config, state_delta=state_delta
        )

        # Handle new and updated collections
        state_delta = self._calculate_added_and_updated_collections(state_delta)
        return state_delta

    def _calculate_added_and_updated_notes(
        self,
        notes: Dict[Any, Note],
        *,
        sync_config: SyncConfig,
        state_delta: StateDelta,
    ) -> StateDelta:
        """
        Calculate added and updated notes from the remote source and update the
        state delta accordingly.

        :param notes: A dictionary of remote notes, keyed by their IDs.
        :param sync_config: The synchronization configuration.
        :param state_delta: The state delta to update with any changes.
        :return: The updated state delta.
        """
        last_sync_time = self._last_sync_vars.get_time(sync_config.plugin)

        for note in notes.values():
            existing_note = self._notes_by_path.get(note.path)

            # Convert remote note to local note
            local_note = self._convert_remote_note_to_local(
                note, sync_config=sync_config, state_delta=state_delta
            )

            # pylint:disable=protected-access
            if existing_note:
                if note.updated_at and note.updated_at.timestamp() <= last_sync_time:
                    # If the note hasn't been updated since the last sync, skip it
                    self.logger.debug(
                        'Skipping note %s from plugin %s, not updated since last sync',
                        note.path,
                        sync_config.plugin,
                    )
                    continue

                # Add the note to the state delta
                state_delta.notes.updated[existing_note.id] = local_note
            else:
                # If the note is new, add it to the state delta
                state_delta.notes.added[local_note.id] = local_note

        return state_delta

    def _calculate_deleted_notes(
        self,
        notes: Dict[Any, Note],
        *,
        sync_config: SyncConfig,
        state_delta: StateDelta,
    ) -> StateDelta:
        """
        Calculate deleted notes from the remote source and update the state
        delta accordingly.

        :param notes: A dictionary of remote notes, keyed by their IDs.
        :param sync_config: The synchronization configuration.
        :param state_delta: The state delta to update with any changes.
        :return: The updated state delta.
        """
        remote_notes = {note.path: note for note in notes.values()}
        locally_synced_notes = {
            note.path: note
            for note in self._get_locally_synced_notes(sync_config).values()
        }

        for path, local_note in locally_synced_notes.items():
            if path not in remote_notes:
                self.logger.info(
                    'Note %s has been deleted from remote source %s. Deleting locally.',
                    local_note.path,
                    sync_config.plugin,
                )
                state_delta.notes.deleted[local_note.id] = local_note

        return state_delta

    def _calculate_added_and_updated_collections(
        self, state_delta: StateDelta
    ) -> StateDelta:
        """
        Calculate added and updated collections from the remote source and update the
        state delta accordingly.

        :param state_delta: The state delta to update with any changes.
        :return: The updated state delta.
        """
        # Expand all notes
        all_notes = {**state_delta.notes.added, **state_delta.notes.updated}
        for note in all_notes.copy().values():
            all_notes.update(
                {
                    n.id: n
                    for n in note.synced_from + note.synced_to + note.conflict_notes
                    if n.id not in all_notes
                }
            )

        # Only keep notes from the current plugin
        all_notes = {
            note.id: note
            for note in all_notes.values()
            if note.plugin == self._plugin_name
        }

        # Extract collections from notes
        all_collections = {}
        for note in all_notes.values():
            collection = note.parent
            while collection:
                if (
                    collection.id not in all_collections
                    and collection.plugin == self._plugin_name
                ):
                    all_collections[collection.id] = collection
                collection = collection.parent

        # Add or update collections in the state delta
        for collection in all_collections.values():
            existing_collection = self._collections_by_path.get(collection.path)
            if existing_collection:
                state_delta.collections.updated[existing_collection.id] = collection
            else:
                state_delta.collections.added[collection.id] = collection

        return state_delta

    def _get_locally_synced_notes(self, sync_config: SyncConfig) -> Dict[Any, Note]:
        """
        Given a sync configuration, retrieves the notes that have been synced
        locally with the given plugin.

        :param sync_config: The synchronization configuration.
        :return: A dictionary of notes that have been synced locally, keyed by
            their IDs.
        """
        return {
            note_id: note
            for note_id, note in self._notes.items()
            if any(
                synced_note.plugin == sync_config.plugin
                for synced_note in note.synced_from
            )
        }

    def _infer_id(self, item: Storable) -> Optional[Any]:
        return item.id

    def _normalize_datetime(
        self, t: Optional[Union[int, float, str, datetime.datetime]]
    ) -> Optional[datetime.datetime]:
        """
        Normalize a timestamp to a datetime object with UTC timezone.
        """
        if t is None:
            return None
        if isinstance(t, (int, float)):
            return datetime.datetime.fromtimestamp(t, tz=datetime.timezone.utc)
        if isinstance(t, str):
            try:
                t = datetime.datetime.fromisoformat(t)
            except ValueError:
                self.logger.warning('Invalid datetime string: %s', t)
                return None

        if t.tzinfo is None:
            return t.replace(tzinfo=tz.tzlocal()).astimezone(datetime.timezone.utc)
        return t.astimezone(datetime.timezone.utc)

    def start_remote_sync(self):
        """
        Start the remote synchronization process.
        """
        if not self.sync_from or self._sync_events[SyncState.SYNCED_REMOTE].is_set():
            self._sync_events[SyncState.SYNCED_REMOTE].set()
            return

        self._unregister_sync_handlers = [
            get_bus().register_handler(
                BaseNoteEvent,
                self._event_handler,
                plugin=sync_config.plugin,
            )
            for sync_config in self.sync_from
        ]

        self.logger.info(
            'Synchronizing remote notes from plugins: %s',
            {config.plugin for config in self.sync_from},
        )

        self._remote_sync()

    def stop_remote_sync(self):
        """
        Stop the remote synchronization process and unregister handlers.
        """
        if self._sync_state != SyncState.READY:
            return

        for unregister in self._unregister_sync_handlers:
            unregister()

        self._unregister_sync_handlers.clear()
        self._sync_events[SyncState.SYNCED_REMOTE].clear()
        self.logger.info('Remote synchronization stopped.')

    def stop(self):
        self.stop_remote_sync()
        self.sync_state = SyncState.UNINITIALIZED

    @abstractmethod
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
        Create a new note. This method should be implemented by subclasses.
        """
        raise NotImplementedError('Subclasses must implement create_note.')

    @abstractmethod
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
        Edit an existing note. This method should be implemented by subclasses.
        """

    @abstractmethod
    @action
    def delete_note(self, note_id: Any, *args, **kwargs):
        """
        Delete a note by its ID. This method should be implemented by subclasses.
        """

    @abstractmethod
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
        Create a new collection. This method should be implemented by subclasses.
        """

    @abstractmethod
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
        Edit an existing collection. This method should be implemented by subclasses.
        """

    @abstractmethod
    @action
    def delete_collection(self, collection_id: Any, *args, **kwargs):
        """
        Delete a collection by its ID. This method should be implemented by subclasses.
        """


__all__ = [
    'SyncMixin',
]
