from marshmallow import fields
from marshmallow.schema import Schema
from marshmallow.validate import OneOf


class DbusSignalSchema(Schema):
    bus = fields.String(
        required=True,
        validate=OneOf(['system', 'session'])
    )

    interface = fields.String(allow_none=True, metadata={
        'description': 'The DBus interface that should be monitored (default: all)'
    })

    path = fields.String(allow_none=True, metadata={
        'description': 'Path of the resource to be monitored (default: all)'
    })

    signal = fields.String(allow_none=True, metadata={
        'description': 'Signal name filter (default: all signals)'
    })

    sender = fields.String(allow_none=True, metadata={
        'description': 'Signal sender filter (default: all senders)'
    })
