from marshmallow import Schema, fields

from platypush.schemas import DateTime


class WallabagSchema(Schema):
    pass


class WallabagAnnotationSchema(WallabagSchema):
    id = fields.Integer(
        required=True,
        dump_only=True,
        metadata={'example': 2345},
    )

    text = fields.String(
        attribute='quote',
        metadata={
            'example': 'Some memorable quote',
        },
    )

    comment = fields.String(
        attribute='text',
        metadata={
            'example': 'My comment on this memorable quote',
        },
    )

    ranges = fields.Function(
        lambda data: [
            [int(r['startOffset']), int(r['endOffset'])] for r in data.get('ranges', [])
        ],
        metadata={
            'example': [[100, 180]],
        },
    )

    created_at = DateTime(
        metadata={
            'description': 'When the annotation was created',
        },
    )

    updated_at = DateTime(
        metadata={
            'description': 'When the annotation was last updated',
        },
    )


class WallabagEntrySchema(WallabagSchema):
    id = fields.Integer(
        required=True,
        dump_only=True,
        metadata={'example': 1234},
    )

    url = fields.URL(
        required=True,
        metadata={
            'description': 'Original URL',
            'example': 'https://example.com/article/some-title',
        },
    )

    preview_picture = fields.URL(
        metadata={
            'description': 'Preview picture URL',
            'example': 'https://example.com/article/some-title.jpg',
        },
    )

    is_archived = fields.Boolean()
    is_starred = fields.Boolean()
    is_public = fields.Boolean()
    mimetype = fields.String(
        metadata={
            'example': 'text/html',
        },
    )

    title = fields.String(
        metadata={
            'description': 'Title of the saved page',
        },
    )

    content = fields.String(
        metadata={
            'description': 'Parsed content',
        }
    )

    language = fields.String(
        metadata={
            'example': 'en',
        }
    )

    annotations = fields.List(fields.Nested(WallabagAnnotationSchema))

    published_by = fields.List(
        fields.String,
        metadata={
            'example': ['Author 1', 'Author 2'],
        },
    )

    tags = fields.Function(
        lambda data: [tag['label'] for tag in data.get('tags', [])],
        metadata={
            'example': ['tech', 'programming'],
        },
    )

    reading_time = fields.Integer(
        metadata={
            'description': 'Estimated reading time, in minutes',
            'example': 10,
        }
    )

    created_at = DateTime(
        metadata={
            'description': 'When the entry was created',
        },
    )

    updated_at = DateTime(
        metadata={
            'description': 'When the entry was last updated',
        },
    )

    starred_at = DateTime(
        metadata={
            'description': 'If the entry is starred, when was it last marked',
        },
    )

    published_at = DateTime(
        metadata={
            'description': 'When the entry was initially published',
        },
    )
