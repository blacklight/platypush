from marshmallow import fields
from marshmallow.schema import Schema

from . import DateTime


class GotifyMessageSchema(Schema):
    title = fields.String(
        metadata=dict(
            description='Message title',
            example='Test title',
        )
    )

    message = fields.String(
        required=True,
        metadata=dict(
            description='Message body (markdown is supported)',
            example='Test message',
        )
    )

    priority = fields.Int(
        missing=0,
        metadata=dict(
            description='Message priority',
            example=2,
        )
    )

    extras = fields.Dict(
        metadata=dict(
            description='Extra payload to be delivered with the message',
            example={
                'home::appliances::lighting::on': {
                    'brightness': 15
                },
                'home::appliances::thermostat::change_temperature': {
                    'temperature': 23
                }
            },
        )
    )

    id = fields.Int(
        required=True,
        dump_only=True,
        metadata=dict(
            description='Message ID',
            example=1,
        )
    )

    appid = fields.Int(
        dump_only=True,
        metadata=dict(
            description='ID of the app that posted the message',
            example=1,
        )
    )

    date = DateTime(
        dump_only=True,
        metadata=dict(
            description='Message date',
        )
    )
