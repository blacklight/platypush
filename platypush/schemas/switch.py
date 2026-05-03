from marshmallow import fields
from marshmallow.schema import Schema


class SwitchStatusSchema(Schema):
    id = fields.Raw(metadata={'description': 'Device unique ID'})
    name = fields.String(required=True, metadata={'description': 'Device name'})
    on = fields.Boolean(
        required=True,
        metadata={'description': 'True if the device is on, False otherwise'},
    )
