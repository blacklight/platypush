from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Iterable

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

    supports_limit: bool = False
    supports_offset: bool = False
