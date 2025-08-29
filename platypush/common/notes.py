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
    conflicting_for: Optional['Note'] = None

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
                **{
                    field: getattr(self, field)
                    for field in self.__dataclass_fields__
                    if not field.startswith('_')
                    and field
                    not in {
                        'parent',
                        'synced_from',
                        'synced_to',
                        'conflict_notes',
                        'conflicting_for',
                    }
                },
                'path': self.path,
                'content_type': self.content_type.value,
                'parent': self.parent.to_dict(minimal=True) if self.parent else None,
                'source': (
                    (
                        self.source.to_dict()
                        if isinstance(self.source, NoteSource)
                        else self.source
                    )
                    if self.source
                    else None
                ),
                'tags': list(self.tags),
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            }

        return NoteItemSchema().dump(  # type: ignore
            {
                **{
                    field: getattr(self, field)
                    for field in self.__dataclass_fields__
                    if not field.startswith('_') and field != 'parent'
                },
                'path': self.path,
                'parent': self.parent.to_dict(minimal=True) if self.parent else None,
                'tags': list(self.tags),
                'synced_from': [
                    note.to_dict(minimal=True) for note in self.synced_from
                ],
                'synced_to': [note.to_dict(minimal=True) for note in self.synced_to],
                'conflict_notes': [
                    note.to_dict(minimal=True) for note in self.conflict_notes
                ],
                'conflicting_for': (
                    self.conflicting_for.to_dict(minimal=True)
                    if self.conflicting_for
                    else None
                ),
            },
        )

    @property
    def is_conflict_note(self) -> bool:
        """
        :return: True if the note is a conflict note (i.e., it is a virtual copy
            of a remote note that has conflicts with a local note). If this is
            true, the ``conflicting_for`` field will point to the local note it
            conflicts with.
        """
        return bool(self.conflicting_for)

    @classmethod
    def build(cls, _visited: Optional[Dict[Any, 'Note']] = None, **kwargs) -> 'Note':
        note = cls(
            **{
                **{k: v for k, v in kwargs.items() if k in cls.__dataclass_fields__},
                'content_type': (
                    NoteContentType.by_extension(kwargs['content_type'])
                    if isinstance(kwargs.get('content_type'), str)
                    else kwargs.get('content_type', NoteContentType.MARKDOWN)
                ),
                'parent': (
                    NoteCollection.build(
                        **{'plugin': kwargs.get('plugin'), **kwargs['parent']}
                    )
                    if kwargs.get('parent')
                    else None
                ),
                'source': (
                    NoteSource(**kwargs['source'])
                    if isinstance(kwargs.get('source'), dict)
                    else kwargs.get('source')
                ),
                'created_at': (
                    datetime.fromisoformat(kwargs['created_at'])
                    if isinstance(kwargs.get('created_at'), str)
                    else kwargs.get('created_at')
                ),
                'updated_at': (
                    datetime.fromisoformat(kwargs['updated_at'])
                    if isinstance(kwargs.get('updated_at'), str)
                    else kwargs.get('updated_at')
                ),
            }
        )

        _visited = _visited or {}
        if note.id in _visited:
            return _visited[note.id]

        _visited[note.id] = note
        for key, notes_args in {
            k: {
                '_visited': _visited,
                'plugin': note.plugin,
                **n,
            }
            for k in ['synced_from', 'synced_to', 'conflict_notes', 'conflicting_for']
            for n in kwargs.get(k, [])
        }.items():
            if note not in getattr(note, key):
                getattr(note, key).append(cls.build(**notes_args))

        return note

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Note):
            return False

        for attr in [
            'id',
            'plugin',
            'title',
            'path',
            'description',
            'digest',
            'tags',
            'author',
            'latitude',
            'longitude',
            'altitude',
            'content_type',
            'source',
        ]:
            if getattr(self, attr) != getattr(other, attr):
                return False

        if (self.parent.id if self.parent else None) != (
            other.parent.id if other.parent else None
        ):
            return False

        return True


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

    def to_dict(self, minimal: bool = False) -> dict:
        if minimal:
            return {
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
            }

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

    @classmethod
    def build(cls, **kwargs) -> 'NoteCollection':
        parent = kwargs.pop('parent', None)
        if parent:
            if isinstance(parent, dict):
                kwargs['parent'] = NoteCollection.build(**parent)
            elif isinstance(parent, NoteCollection):
                kwargs['parent'] = parent

        return cls(
            **{k: v for k, v in kwargs.items() if k in cls.__dataclass_fields__},
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, NoteCollection):
            return False

        for attr in ['id', 'plugin', 'title', 'path', 'description']:
            if getattr(self, attr) != getattr(other, attr):
                return False

        if (self.parent.id if self.parent else None) != (
            other.parent.id if other.parent else None
        ):
            return False

        return True
