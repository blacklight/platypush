from abc import ABC
from marshmallow import INCLUDE, Schema, fields, post_dump

from platypush.schemas import DateTime


def _note_minimal(data, **_) -> dict:
    """
    Generate a minimal representation of the note for nested outputs.
    """

    def get_attr(obj, attr, default=None):
        if not obj:
            return default
        if isinstance(obj, dict):
            return obj.get(attr, default)
        return getattr(obj, attr, default)

    return {
        'id': get_attr(data, 'id'),
        'title': get_attr(data, 'title'),
        'description': get_attr(data, 'description'),
        'plugin': get_attr(data, 'plugin'),
        'path': get_attr(data, 'path'),
        'digest': get_attr(data, 'digest'),
    }


class BaseNoteSchema(Schema, ABC):
    """
    Base schema for note objects.
    """

    # pylint: disable=too-few-public-methods
    class Meta:  # type: ignore
        """
        Meta class for the schema.
        """

        unknown = INCLUDE


class NoteSourceSchema(BaseNoteSchema):
    """
    Schema for a note source, such as a URL or file path.
    """

    name = fields.String(
        metadata={
            'description': 'Name of the source',
            'example': 'My Note Source',
        },
    )

    url = fields.String(
        metadata={
            'description': 'URL of the source',
            'example': 'https://example.com/note',
        },
    )

    app = fields.String(
        metadata={
            'description': 'Application associated with the source',
            'example': 'My Note App',
        },
    )


class NoteItemSchema(BaseNoteSchema):
    """
    Schema for a note object.
    """

    id = fields.Raw(
        required=True,
        dump_only=True,
        metadata={'example': 2345},
    )

    title = fields.String(
        metadata={
            'description': 'Title of the note',
            'example': 'My Important Note',
        },
    )

    path = fields.String(
        dump_only=True,
        metadata={
            'description': 'Path to the note file',
            'example': '/notes/my_important_note.md',
        },
    )

    content = fields.String(
        metadata={
            'example': 'Note content goes here',
        },
    )

    content_type = fields.Function(
        lambda data: (
            data.content_type.value
            if hasattr(data, 'content_type')
            else (data or {}).get('content_type')
        ),
        metadata={
            'description': 'Content type of the note (e.g., txt, md, html)',
            'example': 'md',
        },
    )

    description = fields.String(
        metadata={
            'description': 'Description of the note',
            'example': 'This note contains important information.',
        },
    )

    digest = fields.String(
        dump_only=True,
        metadata={
            'description': 'Unique digest of the note content',
            'example': 'abc123def456',
        },
    )

    parent = fields.Nested(
        'NoteCollectionSchema',
        dump_only=True,
        metadata={
            'description': 'Parent note collection',
            'example': {
                'id': 1234,
                'title': 'My Notes',
                'description': 'A collection of my important notes',
            },
        },
    )

    source = fields.Nested(
        NoteSourceSchema,
        metadata={
            'description': 'Source of the note, such as a URL or file path',
            'example': {
                'name': 'My Note Source',
                'url': 'https://example.com/note',
                'app': 'My Note App',
            },
        },
    )

    author = fields.String(
        metadata={
            'description': 'Author of the note',
            'example': 'John Doe',
        },
    )

    latitude = fields.Float(
        metadata={
            'description': 'Latitude of the note location',
            'example': 37.7749,
        },
    )

    longitude = fields.Float(
        metadata={
            'description': 'Longitude of the note location',
            'example': -122.4194,
        },
    )

    altitude = fields.Float(
        metadata={
            'description': 'Altitude of the note location',
            'example': 30.0,
        },
    )

    tags = fields.List(
        fields.String(),
        metadata={
            'description': 'List of tags associated with the note',
            'example': ['important', 'work'],
        },
    )

    synced_from = fields.Function(
        lambda data: [
            _note_minimal(note)
            for note in (
                getattr(data, 'synced_from', (data or {}).get('synced_from')) or []
            )
        ],
        dump_only=True,
        metadata={
            'description': 'List of notes this note was synced from',
            'example': [
                {
                    'id': 1236,
                    'title': 'Synced Note',
                    'plugin': 'sync_plugin1',
                },
            ],
        },
    )

    synced_to = fields.Function(
        lambda data: [
            _note_minimal(note)
            for note in (
                getattr(data, 'synced_to', (data or {}).get('synced_to')) or []
            )
        ],
        dump_only=True,
        metadata={
            'description': 'List of notes this note was synced to',
            'example': [
                {
                    'id': 1237,
                    'title': 'Synced Note',
                    'plugin': 'sync_plugin2',
                },
            ],
        },
    )

    conflict_notes = fields.Function(
        lambda data: [
            _note_minimal(note)
            for note in (
                getattr(data, 'conflict_notes', (data or {}).get('conflict_notes'))
                or []
            )
        ],
        dump_only=True,
        metadata={
            'description': 'List of notes that are in conflict with this note',
            'example': [
                {
                    'id': 1238,
                    'title': 'Conflict Note',
                    'plugin': 'sync_plugin3',
                },
            ],
        },
    )

    created_at = DateTime(
        metadata={
            'description': 'When the note was created',
        },
    )

    updated_at = DateTime(
        metadata={
            'description': 'When the note was last updated',
        },
    )

    @post_dump
    def compact_related_notes(self, data: dict, **_) -> dict:
        """
        Compact the related notes in the output to only include minimal information.
        """
        from platypush.common.notes import Note

        if 'sync_from' in data:
            data['sync_from'] = [
                Note(**note).to_dict(minimal=True) for note in data['sync_from']
            ]
        if 'sync_to' in data:
            data['sync_to'] = [
                Note(**note).to_dict(minimal=True) for note in data['sync_to']
            ]
        if data.get('conflict_note'):
            data['conflict_note'] = Note(**data['conflict_note']).to_dict(minimal=True)

        return data


class NoteCollectionSchema(BaseNoteSchema):
    """
    Schema for a collection of notes.
    """

    id = fields.Raw(
        dump_only=True,
        metadata={'example': 1234},
    )

    title = fields.String(
        metadata={
            'description': 'Title of the note collection',
            'example': 'My Notes',
        },
    )

    description = fields.String(
        metadata={
            'description': 'Description of the note collection',
            'example': 'A collection of my important notes',
        },
    )

    path = fields.String(
        dump_only=True,
        metadata={
            'description': 'Path to the note file',
            'example': '/notes/subfolder',
        },
    )

    parent = fields.Nested(
        'NoteCollectionSchema',
        metadata={
            'description': 'Parent note collection',
            'example': {
                'id': 1233,
                'title': 'All Notes',
                'description': 'A top-level collection of all notes',
            },
        },
    )

    collections = fields.List(
        fields.Nested('NoteCollectionSchema'),
        metadata={
            'description': 'List of sub-collections',
            'example': [
                {
                    'id': 1235,
                    'title': 'Work Notes',
                    'description': 'Notes related to work projects',
                },
            ],
        },
    )

    notes = fields.List(
        fields.Nested(NoteItemSchema),
        metadata={
            'description': 'List of notes',
            'example': [
                {
                    'id': 2345,
                    'title': 'My Important Note',
                    'content': 'Note content goes here',
                    'created_at': '2023-10-01T12:00:00Z',
                    'updated_at': '2023-10-02T12:00:00Z',
                },
            ],
        },
    )

    created_at = DateTime(
        metadata={
            'description': 'When the note collection was created',
        },
    )

    updated_at = DateTime(
        metadata={
            'description': 'When the note collection was last updated',
        },
    )
