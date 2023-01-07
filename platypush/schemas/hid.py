from marshmallow import fields, Schema, INCLUDE


class HidDeviceSchema(Schema):
    class Meta:
        unknown = INCLUDE

    path = fields.String(
        metadata={
            'description': 'Path to the raw HID device',
            'example': '/dev/hidraw0',
        },
    )

    serial_number = fields.String(
        metadata={
            'description': 'Serial number',
            'example': '00:11:22:33:44:55',
        },
    )

    vendor_id = fields.Integer(
        metadata={
            'description': 'Vendor ID',
            'example': 1234,
        },
    )

    product_id = fields.Integer(
        metadata={
            'description': 'Product ID',
            'example': 4321,
        },
    )

    manufacturer_string = fields.String(
        metadata={
            'description': 'Manufacturer custom string',
            'example': 'foo',
        },
    )

    product_string = fields.String(
        metadata={
            'description': 'Main name of the product',
            'example': 'My Device',
        },
    )


class HidMonitoredDeviceSchema(HidDeviceSchema):
    notify_only_if_changed = fields.Boolean(
        load_default=True,
        metadata={
            'description': 'If set to true (default), only changes in the '
            'values of the device will trigger events. So if you are e.g. '
            'monitoring the state of a joystick, only changes in the pressed '
            'buttons will trigger events.',
        },
    )

    data_size = fields.Integer(
        load_default=64,
        metadata={
            'description': 'How many bytes should be read from the device on '
            'each iteration (default: 64)',
        },
    )

    poll_seconds = fields.Float(
        load_default=0,
        metadata={
            'description': 'How often we should wait before data reads '
            '(default: no wait)'
        },
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for attr in (
            'path',
            'serial_number',
            'vendor_id',
            'product_id',
            'manufacturer_string',
            'product_string',
        ):
            self._declared_fields[attr].metadata['description'] += ' (optional)'
