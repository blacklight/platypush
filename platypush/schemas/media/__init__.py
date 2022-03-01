from marshmallow import fields
from marshmallow.schema import Schema


class MediaCollectionSchema(Schema):
    id = fields.String(
        metadata=dict(
            description='Collection ID',
        )
    )

    name = fields.String(
        required=True,
        metadata=dict(
            description='Collection name',
        )
    )

    type = fields.String(
        metadata=dict(
            description='Collection type (movies, music, series etc.)',
        )
    )

    image = fields.URL(
        metadata=dict(
            description='Collection image (URL)',
        )
    )


class MediaArtistSchema(Schema):
    id = fields.String(
        metadata=dict(
            description='Artist ID',
        )
    )

    name = fields.String(
        required=True,
        metadata=dict(
            description='Artist name',
        )
    )

    image = fields.URL(
        metadata=dict(
            description='Artist main image (URL)',
        )
    )


class MediaItemSchema(Schema):
    id = fields.String()
    title = fields.String(required=True)
    url = fields.URL()
    file = fields.String()
    image = fields.URL()


class MediaVideoSchema(MediaItemSchema):
    year = fields.Integer()
    has_subtitles = fields.Boolean()


class MediaMovieSchema(MediaItemSchema):
    pass


class MediaEpisodeSchema(MediaItemSchema):
    pass

