from marshmallow import EXCLUDE, fields
from marshmallow.schema import Schema


class JoystickStateSchema(Schema):
    """
    Joystick state schema.
    """

    left_joystick_y = fields.Float(
        metadata={
            'description': 'Left joystick Y axis value',
            'example': 0.5,
        }
    )

    left_joystick_x = fields.Float(
        metadata={
            'description': 'Left joystick X axis value',
            'example': 0.5,
        }
    )

    right_joystick_y = fields.Float(
        metadata={
            'description': 'Right joystick Y axis value',
            'example': 0.5,
        }
    )

    right_joystick_x = fields.Float(
        metadata={
            'description': 'Right joystick X axis value',
            'example': 0.5,
        }
    )

    left_trigger = fields.Float(
        metadata={
            'description': 'Left trigger value',
            'example': 0.5,
        }
    )

    right_trigger = fields.Float(
        metadata={
            'description': 'Right trigger value',
            'example': 0.5,
        }
    )

    left_bumper = fields.Integer(
        metadata={
            'description': 'Left bumper state',
            'example': 1,
        }
    )

    right_bumper = fields.Integer(
        metadata={
            'description': 'Right bumper state',
            'example': 1,
        }
    )

    a = fields.Integer(
        metadata={
            'description': 'A button state',
            'example': 1,
        }
    )

    x = fields.Integer(
        metadata={
            'description': 'X button state',
            'example': 1,
        }
    )

    y = fields.Integer(
        metadata={
            'description': 'Y button state',
            'example': 1,
        }
    )

    b = fields.Integer(
        metadata={
            'description': 'B button state',
            'example': 1,
        }
    )

    left_thumb = fields.Integer(
        metadata={
            'description': 'Left thumb button state',
            'example': 1,
        }
    )

    right_thumb = fields.Integer(
        metadata={
            'description': 'Right thumb button state',
            'example': 1,
        }
    )

    back = fields.Integer(
        metadata={
            'description': 'Back button state',
            'example': 1,
        }
    )

    start = fields.Integer(
        metadata={
            'description': 'Start button state',
            'example': 1,
        }
    )

    left_dir_pad = fields.Integer(
        metadata={
            'description': 'Left direction pad button state',
            'example': 1,
        }
    )

    right_dir_pad = fields.Integer(
        metadata={
            'description': 'Right direction pad button state',
            'example': 1,
        }
    )

    up_dir_pad = fields.Integer(
        metadata={
            'description': 'Up direction pad button state',
            'example': 1,
        }
    )

    down_dir_pad = fields.Integer(
        metadata={
            'description': 'Down direction pad button state',
            'example': 1,
        }
    )


class JoystickDeviceSchema(Schema):
    """
    Joystick device schema.
    """

    class Meta:
        """
        Meta class.
        """

        unknown = EXCLUDE

    name = fields.String(
        metadata={
            'description': 'Joystick name',
            'example': 'Xbox 360 Controller',
        }
    )

    path = fields.Function(
        lambda obj: obj.get_char_device_path(),
        metadata={
            'description': 'Joystick character device path',
            'example': '/dev/input/event0',
        },
    )

    number = fields.Integer(
        metadata={
            'description': 'Joystick number',
            'example': 0,
        }
    )

    protocol = fields.String(
        metadata={
            'description': 'Joystick protocol',
            'example': 'usb',
        }
    )


class JoystickStatusSchema(Schema):
    """
    Joystick status schema.
    """

    device = fields.Nested(JoystickDeviceSchema, required=True)
    state = fields.Nested(JoystickStateSchema, required=True)
