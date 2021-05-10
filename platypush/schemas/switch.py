from marshmallow import fields
from marshmallow.schema import Schema


class SwitchStatusSchema(Schema):
    id = fields.Raw(metadata=dict(description='Device unique ID'))
    name = fields.String(required=True, metadata=dict(description='Device name'))
    on = fields.Boolean(required=True, metadata=dict(description='True if the device is on, False otherwise'))
