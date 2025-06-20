from dataclasses import dataclass, field
from typing import Any, Dict

from platypush.common.notes import Note, NoteCollection


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
