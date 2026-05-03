from marshmallow import fields, INCLUDE
from marshmallow.schema import Schema

from platypush.schemas import StrippedString


class SlackMessageBlockSchema(Schema):
    class Meta:
        unknown = INCLUDE

    type = fields.String(required=True, metadata={'description': 'Message block type'})
    block_id = fields.String(required=True, metadata={'description': 'Block ID'})


class SlackMessageIconSchema(Schema):
    image_36 = fields.URL()
    image_48 = fields.URL()
    image_72 = fields.URL()


class SlackMessageSchema(Schema):
    text = StrippedString(required=True, metadata={'description': 'Message text'})
    user = fields.String(
        required=True, metadata={'description': 'User ID of the sender'}
    )
    channel = fields.String(
        metadata={'description': 'Channel ID associated with the message'}
    )
    team = fields.String(
        metadata={'description': 'Team ID associated with the message'}
    )
    timestamp = fields.DateTime(metadata={'description': 'Date and time of the event'})
    icons = fields.Nested(SlackMessageIconSchema)
    blocks = fields.Nested(SlackMessageBlockSchema, many=True)
    previous_message = fields.Nested(
        'SlackMessageSchema',
        metadata={
            'description': 'For received replies, it includes the parent message in the reply chain. '
            'For edited messages, it contains the previous version.'
        },
    )
