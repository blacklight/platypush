from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
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


class NoteContentType(Enum):
    """
    Enum representing the content type of a note.
    """

    TEXT = 'txt'
    MARKDOWN = 'md'
    HTML = 'html'

    @property
    def mime_type(self) -> str:
        if self.value == 'txt':
            return 'text/plain'
        if self.value == 'md':
            return 'text/markdown'
        return f'text/{self.value}'

    @classmethod
    def by_extension(cls, ext: str) -> 'NoteContentType':
        """
        Get the content type by file extension.
        """
        ext = ext.lower().strip('.')
        for content_type in cls:
            if content_type.value == ext:
                return content_type

        return cls.TEXT  # Default to TEXT if no match found


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
    content_type: NoteContentType = NoteContentType.MARKDOWN
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
    synced_from: List['Note'] = field(default_factory=list)
    synced_to: List['Note'] = field(default_factory=list)
    conflict_notes: List['Note'] = field(default_factory=list)

    def __post_init__(self):
        """
        Post-initialization to update the digest if content is provided.
        """
        self._update_digest()

    @property
    def path(self) -> str:
        return (
            self.parent.path if self.parent else '/'
        ) + f'{self.title}.{self.content_type.value}'

    def _update_digest(self) -> Optional[str]:
        if self.content and not self.digest:
            self.digest = sha256(self.content.encode('utf-8')).hexdigest()
        return self.digest

    def __setattr__(self, name: str, value: Any, /) -> None:
        if name == 'content':
            value = value or ''

        super().__setattr__(name, value)
        if name == 'content':
            self._update_digest()

    def to_dict(self, minimal: bool = False) -> dict:
        if minimal:
            return {
                'id': self.id,
                'title': self.title,
                'description': self.description,
                'plugin': self.plugin,
                'path': self.path,
                'content_type': self.content_type.value,
                'digest': self.digest,
                'latitude': self.latitude,
                'longitude': self.longitude,
                'altitude': self.altitude,
                'author': self.author,
                'source': self.source.to_dict() if self.source else None,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'updated_at': self.updated_at.isoformat() if self.updated_at else None,
                'tags': list(self.tags),
            }

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

    @property
    def path(self) -> str:
        """
        Generate the path for the collection based on its hierarchy.
        """
        path = []
        parent = self.parent
        while parent:
            path.append(parent.title)
            parent = parent.parent

        return ('/' + '/'.join(reversed([self.title, *path])) + '/').replace('//', '/')

    def to_dict(self) -> dict:
        return NoteCollectionSchema().dump(  # type: ignore
            {
                **{
                    field: getattr(self, field)
                    for field in self.__dataclass_fields__
                    if not field.startswith('_') and field != 'parent'
                },
                'path': self.path,
                'parent': (
                    {
                        'id': self.parent.id,
                        'title': self.parent.title,
                        'path': self.parent.path,
                    }
                    if self.parent
                    else None
                ),
                'collections': [
                    collection.to_dict() for collection in self.collections
                ],
                'notes': [note.to_dict(minimal=True) for note in self.notes],
            }
        )
