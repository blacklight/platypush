from marshmallow import fields
from marshmallow.schema import Schema

from platypush.schemas import DateTime


class RssFeedEntrySchema(Schema):
    feed_title = fields.String(metadata={'description': 'Feed title'})
    feed_url = fields.URL(
        required=True,
        metadata={
            'description': 'URL of the feed',
            'example': 'https://some-website/rss',
        },
    )

    id = fields.String(
        required=True,
        metadata={
            'description': 'Feed entry ID',
            'example': '1234',
        },
    )

    url = fields.URL(
        required=True,
        metadata={
            'description': 'URL of the feed entry',
            'example': 'https://some-website/articles/1234',
        },
    )

    published = DateTime(
        required=True, metadata={'description': 'Entry published time'}
    )

    title = fields.String(metadata={'description': 'Feed entry title'})
    summary = fields.String(metadata={'description': 'Feed entry summary'})
    content = fields.String(metadata={'description': 'Feed entry content'})
    author = fields.String(metadata={'description': 'Feed entry author'})
    tags = fields.List(
        fields.String(),
        metadata={'description': 'Feed entry tags'},
    )
