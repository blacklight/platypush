from abc import ABC
from marshmallow import INCLUDE, Schema, fields

from platypush.schemas import DateTime


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

    content = fields.String(
        metadata={
            'example': 'Note content goes here',
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
