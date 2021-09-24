from marshmallow import fields
from marshmallow.schema import Schema
from marshmallow.validate import OneOf


class NgrokTunnelSchema(Schema):
    name = fields.String(
        metadata=dict(
            description='Tunnel friendly name or auto-generated name',
            example='tcp-8080-my-tunnel',
        )
    )

    protocol = fields.String(
        allow_none=False,
        attribute='proto',
        validate=OneOf(['tcp', 'udp', 'http']),
        metadata=dict(
            description='Tunnel protocol',
            example='tcp',
        ),
    )

    url = fields.String(
        attribute='public_url',
        required=True,
        metadata=dict(
            description='Public URL to the ngrok tunnel',
            example='tcp://8.tcp.ngrok.io:12345',
        )
    )
