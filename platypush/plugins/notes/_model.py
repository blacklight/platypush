from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, IntEnum
from typing import Any, Dict, Iterable, Optional

from platypush.common.notes import Note, NoteCollection, Serializable, Storable


@dataclass
class NotesDelta:
    """
    Represents a delta of changes in notes.
    """

    added: Dict[Any, Note] = field(default_factory=dict)
    updated: Dict[Any, Note] = field(default_factory=dict)
    deleted: Dict[Any, Note] = field(default_factory=dict)

    def is_empty(self) -> bool:
        """
        Check if the delta is empty (no added, updated, or deleted notes).
        """
        return not (self.added or self.updated or self.deleted)

    def __str__(self):
        """
        String representation of the NotesDelta.
        """
        return (
            f'NotesDelta(added={len(self.added)}, '
            f'updated={len(self.updated)}, '
            f'deleted={len(self.deleted)})'
        )


@dataclass
class CollectionsDelta:
    """
    Represents a delta of changes in note collections.
    """

    added: Dict[Any, NoteCollection] = field(default_factory=dict)
    updated: Dict[Any, NoteCollection] = field(default_factory=dict)
    deleted: Dict[Any, NoteCollection] = field(default_factory=dict)

    def is_empty(self) -> bool:
        """
        Check if the delta is empty (no added, updated, or deleted collections).
        """
        return not (self.added or self.updated or self.deleted)

    def __str__(self):
        """
        String representation of the CollectionsDelta.
        """
        return (
            f'CollectionsDelta(added={len(self.added)}, '
            f'updated={len(self.updated)}, '
            f'deleted={len(self.deleted)})'
        )


@dataclass
class StateDelta:
    """
    Represents a delta of changes in the state of notes and collections.
    """

    notes: NotesDelta = field(default_factory=NotesDelta)
    collections: CollectionsDelta = field(default_factory=CollectionsDelta)
    latest_updated_at: float = 0

    def is_empty(self) -> bool:
        """
        Check if the state delta is empty (no changes in notes or collections).
        """
        return self.notes.is_empty() and self.collections.is_empty()

    def __str__(self):
        """
        String representation of the StateDelta.
        """
        last_updated_at_str = (
            datetime.fromtimestamp(self.latest_updated_at).isoformat()
            if self.latest_updated_at
            else "None"
        )

        return (
            f'StateDelta(notes={self.notes}, '
            f'collections={self.collections}, '
            f'latest_updated_at={last_updated_at_str})'
        )


class ItemType(Enum):
    """
    Enum representing the type of item.
    """

    NOTE = 'note'
    COLLECTION = 'collection'
    TAG = 'tag'


@dataclass
class Item(Serializable):
    """
    Represents a generic note item.
    """

    type: ItemType
    item: Storable

    def __post_init__(self):
        """
        Validate the item type after initialization.
        """
        if not isinstance(self.type, ItemType):
            raise ValueError(f'Invalid item type: {self.type}')

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the item to a dictionary representation.
        """
        return {
            'type': self.type.value,
            'item': self.item.to_dict(),
        }


@dataclass
class Results(Serializable):
    """
    Represents a collection of results, which can include notes, collections, and tags.
    """

    items: Iterable[Item] = field(default_factory=list)
    has_more: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the results to a dictionary representation.
        """
        return {
            'results': [item.to_dict() for item in self.items],
            'has_more': self.has_more,
        }


@dataclass
class ApiSettings:
    """
    Represents plugin-specific API settings.
    """

    supports_notes_limit: bool = False
    supports_notes_offset: bool = False
    supports_collections_limit: bool = False
    supports_collections_offset: bool = False
    supports_search_limit: bool = False
    supports_search_offset: bool = False
    supports_search: bool = False


class ResultsType(Enum):
    """
    Enum representing the type of results.
    """

    NOTES = 'notes'
    COLLECTIONS = 'collections'
    SEARCH = 'search'


class SyncState(IntEnum):
    """
    Enum for defining the state of synchronization.
    """

    UNINITIALIZED = 0
    """The synchronization state has not been initialized."""
    SYNCING_LOCAL = 1
    """The local synchronization is being performed."""
    SYNCED_LOCAL = 2
    """The plugin has pulled local data and is ready to synchronize notes."""
    SYNCING_REMOTE = 3
    """The remote synchronization is being performed."""
    SYNCED_REMOTE = 4
    """The plugin has pulled remote data and is ready to synchronize notes."""
    READY = 5
    """The plugin has pulled both local and remote data."""


class SyncConflictResolution(Enum):
    """
    Enum for defining how to resolve synchronization conflicts.
    """

    OVERWRITE = "overwrite"
    """Overwrite the local version of the note with the remote version."""
    MERGE = "merge"
    """
    Attempt a merge the local and remote versions of the note, and save the
    remote version to a temporary file following the naming template
    ``__CONFLICT__[{remote_note_plugin}]{remote_note.title}.{ext}``.
    """
    IGNORE = "ignore"
    """Ignore the conflict and do not update the note."""


@dataclass
class SyncConfig:
    """
    Configuration for synchronization settings.
    """

    plugin: str
    """The name of the plugin to subscribe to for synchronization."""
    conflict_resolution: SyncConflictResolution = SyncConflictResolution.MERGE
    """The strategy to resolve conflicts during synchronization."""
    pull_remote: bool = True
    """
    If set to True, the plugin will pull all the notes from the remote upon
    initialization. If set to False, the plugin will only synchronize changes
    processed while it is running.
    """
    timeout: Optional[float] = 30
    """
    The timeout in seconds for synchronization operations. If None, no
    timeout is applied.
    """
