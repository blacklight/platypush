from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from hashlib import md5, sha256
from typing import Any, Dict, List, Optional, Set
from uuid import UUID

from platypush.message import JSONAble
from platypush.schemas.notes import NoteCollectionSchema, NoteItemSchema


class Serializable(JSONAble, ABC):
    """
    Base class for serializable objects.
    """

    @abstractmethod
    def to_dict(self) -> dict:
        """
        Convert the object to a dictionary representation.
        """

    def to_json(self) -> dict:
        return self.to_dict()


@dataclass
class Storable(Serializable, ABC):
    """
    Base class for note objects that can be represented as databases entries.
    """

    id: Any
    plugin: str

    @property
    def _db_id(self) -> UUID:
        """
        Generate a deterministic UUID based on the note's plugin and ID.
        """
        key = f'{self.plugin}:{self.id}'
        digest = md5(key.encode()).digest()
        return UUID(int=int.from_bytes(digest, 'little'))


@dataclass
class NoteSource(Serializable):
    """
    Represents a source for a note, such as a URL or file path.
    """

    name: Optional[str] = None
    url: Optional[str] = None
    app: Optional[str] = None

    def to_dict(self) -> dict:
        return self.__dict__


@dataclass
class Note(Storable):
    """
    Represents a note with a title and content.
    """

    title: str
    description: Optional[str] = None
    content: Optional[str] = None
    parent: Optional['NoteCollection'] = None
    tags: Set[str] = field(default_factory=set)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    digest: Optional[str] = field(default=None)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    altitude: Optional[float] = None
    author: Optional[str] = None
    source: Optional[NoteSource] = None
    _path: Optional[str] = None

    def __post_init__(self):
        """
        Post-initialization to update the digest if content is provided.
        """
        self.digest = self._update_digest()

    @property
    def path(self) -> str:
        # If the path is already set, return it
        if self._path:
            return self._path

        # Recursively build the path by expanding the parent collections
        path = []
        parent = self.parent
        while parent:
            path.append(parent.title)
            parent = parent.parent

        return '/'.join(reversed(path)) + f'/{self.title}.md'

    @path.setter
    def path(self, value: str):
        """
        Set the path for the note.
        """
        self._path = value

    def _update_digest(self) -> Optional[str]:
        if self.content and not self.digest:
            self.digest = sha256(self.content.encode('utf-8')).hexdigest()
        return self.digest

    def to_dict(self) -> dict:
        return NoteItemSchema().dump(  # type: ignore
            {
                **{
                    field: getattr(self, field)
                    for field in self.__dataclass_fields__
                    if not field.startswith('_') and field != 'parent'
                },
                'path': self.path,
                'parent': (
                    {
                        'id': self.parent.id if self.parent else None,
                        'title': self.parent.title if self.parent else None,
                    }
                    if self.parent
                    else None
                ),
            },
        )


@dataclass
class NoteCollection(Storable):
    """
    Represents a collection of notes.
    """

    title: str
    description: Optional[str] = None
    parent: Optional['NoteCollection'] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    _notes: Dict[Any, Note] = field(default_factory=dict)
    _collections: Dict[Any, 'NoteCollection'] = field(default_factory=dict)

    @property
    def notes(self) -> List[Note]:
        return list(self._notes.values())

    @property
    def collections(self) -> List['NoteCollection']:
        return list(self._collections.values())

    def to_dict(self) -> dict:
        return NoteCollectionSchema().dump(  # type: ignore
            {
                **{
                    field: getattr(self, field)
                    for field in self.__dataclass_fields__
                    if not field.startswith('_') and field != 'parent'
                },
                'parent': (
                    {
                        'id': self.parent.id,
                        'title': self.parent.title,
                    }
                    if self.parent
                    else None
                ),
                'collections': [
                    collection.to_dict() for collection in self.collections
                ],
                'notes': [
                    {
                        field: getattr(note, field)
                        for field in [*note.__dataclass_fields__, 'digest']
                        if field not in ['parent', 'content']
                    }
                    for note in self.notes
                ],
            }
        )
