from marshmallow import fields
from marshmallow.schema import Schema


class PingResponseSchema(Schema):
    """
    Ping response schema.
    """

    host = fields.String(
        required=True,
        metadata={
            "description": "Remote host IP or name",
            "example": "platypush.tech",
        },
    )

    success = fields.Boolean(
        required=True,
        metadata={
            "description": "True if the ping was successful, False otherwise",
            "example": True,
        },
    )

    min = fields.Float(
        required=False,
        metadata={
            "description": "Minimum round-trip time (in ms)",
            "example": 0.1,
        },
    )

    max = fields.Float(
        required=False,
        metadata={
            "description": "Maximum round-trip time (in ms)",
            "example": 0.2,
        },
    )

    avg = fields.Float(
        required=False,
        metadata={
            "description": "Average round-trip time (in ms)",
            "example": 0.15,
        },
    )

    mdev = fields.Float(
        required=False,
        metadata={
            "description": "Standard deviation of the round-trip time (in ms)",
            "example": 0.05,
        },
    )
