from marshmallow import fields
from marshmallow.schema import Schema

from . import DateTime


class GotifyMessageSchema(Schema):
    title = fields.String(
        metadata={
            'description': 'Message title',
            'example': 'Test message',
        }
    )

    message = fields.String(
        required=True,
        metadata={
            'description': 'Message body (Markdown supported)',
            'example': 'This is a test message',
        },
    )

    priority = fields.Int(
        load_default=0,
        metadata={
            'description': 'Message priority (0-5)',
            'example': 2,
        },
    )

    extras = fields.Dict(
        metadata={
            'description': 'Extra payload to be delivered with the message',
            'example': {
                'home::appliances::lighting::on': {'brightness': 15},
                'home::appliances::thermostat::change_temperature': {'temperature': 23},
            },
        }
    )

    id = fields.Int(
        required=True,
        dump_only=True,
        metadata={
            'description': 'Message ID',
            'example': 1,
        },
    )

    appid = fields.Int(
        dump_only=True,
        metadata={
            'description': 'ID of the app that posted the message',
            'example': 1,
        },
    )

    date = DateTime(
        dump_only=True,
        metadata={
            'description': 'Message date',
        },
    )
