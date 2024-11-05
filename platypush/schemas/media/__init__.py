from marshmallow import fields
from marshmallow.schema import Schema

from platypush.schemas import DateTime


class MediaCollectionSchema(Schema):
    id = fields.String(
        metadata={
            'description': 'Collection ID',
        }
    )

    name = fields.String(
        required=True,
        metadata={
            'description': 'Collection name',
        },
    )

    type = fields.String(
        metadata={
            'description': 'Collection type (movies, music, series etc.)',
        }
    )

    image = fields.URL(
        metadata={
            'description': 'Collection image (URL)',
        }
    )

    path = fields.String(
        metadata={
            'description': 'Path to collection',
        }
    )

    created_at = DateTime(
        metadata={
            'description': 'Creation date',
        }
    )


class MediaArtistSchema(Schema):
    id = fields.String(
        metadata={
            'description': 'Artist ID',
        }
    )

    name = fields.String(
        required=True,
        metadata={
            'description': 'Artist name',
        },
    )

    image = fields.URL(
        metadata={
            'description': 'Artist main image (URL)',
        }
    )

    created_at = DateTime(
        metadata={
            'description': 'Creation date',
        }
    )


class MediaItemSchema(Schema):
    id = fields.String()
    title = fields.String(required=True)
    url = fields.URL()
    file = fields.String()
    image = fields.URL()
    path = fields.String()
    created_at = DateTime(
        metadata={
            'description': 'Creation date',
        }
    )


class MediaVideoSchema(MediaItemSchema):
    year = fields.Integer()
    has_subtitles = fields.Boolean()


class MediaMovieSchema(MediaItemSchema):
    pass


class MediaEpisodeSchema(MediaItemSchema):
    pass
