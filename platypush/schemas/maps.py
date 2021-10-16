from marshmallow import fields, INCLUDE
from marshmallow.schema import Schema


class MapsDistanceSchema(Schema):
    text = fields.String(required=True, metadata=dict(
        description='Distance expressed as readable text',
        example='6.5 km',
    ))

    value = fields.Number(required=True, metadata=dict(
        description='Distance expressed as a numeric value according to the selected units',
        example=6542,
    ))


class MapsDurationSchema(Schema):
    text = fields.String(required=True, metadata=dict(
        description='Duration expressed as readable text',
        example='13 mins',
    ))

    value = fields.Number(required=True, metadata=dict(
        description='Duration expressed in seconds',
        example=777,
    ))


class MapsTravelTimeSchema(Schema):
    class Meta:
        unknown = INCLUDE

    distance = fields.Nested(MapsDistanceSchema)
    duration = fields.Nested(MapsDurationSchema)
