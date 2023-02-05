from marshmallow import fields, EXCLUDE
from marshmallow.schema import Schema
from marshmallow.validate import Range


device_types = [
    'Hub',
    'Hub Plus',
    'Hub Mini',
    'Bot',
    'Curtain',
    'Plug',
    'Meter',
    'Humidifier',
    'Smart Fan',
    'Air Conditioner',
    'TV',
    'Light',
    'IPTV / Streamer',
    'Set Top Box',
    'DVD',
    'Fan',
    'Projector',
    'Camera',
    'Air Purifier',
    'Speaker',
    'Water Heater',
    'Vacuum Cleaner',
    'Remote',
    'Others',
]

remote_types = [
    'Air Conditioner',
    'TV',
    'Light',
    'IPTV / Streamer',
    'Set Top Box',
    'DVD',
    'Fan',
    'Projector',
    'Camera',
    'Air Purifier',
    'Speaker',
    'Water Heater',
    'Vacuum Cleaner',
    'Others',
]


class ColorField(fields.Field):
    """
    Utility field class for color values.
    """

    def _serialize(self, value: str, *_, **__):
        """
        Convert a hex native color value (``ff0000``) to the format exposed by
        the SwitchBot API (``255:0:0``).
        """
        if not value:
            return None
        # fmt: off
        return ''.join([f'{int(i):02x}' for i in value.split(':')])

    def _deserialize(self, value: str, *_, **__):
        """
        Convert a SwitchBot API color value (``255:0:0``) to the hex native
        format (``ff0000``).
        """
        if not value:
            return None

        value = value.lstrip('#')
        # fmt: off
        return ':'.join(
            [str(int(value[i:i+2], 16)) for i in range(0, len(value) - 1, 2)]
        )


class DeviceSchema(Schema):
    """
    Base class for SwitchBot device schemas.
    """

    class Meta:
        """
        Ignore unknown fields.
        """

        unknown = EXCLUDE

    id = fields.String(
        attribute='deviceId',
        required=True,
        metadata={'description': 'Device unique ID'},
    )
    name = fields.String(
        attribute='deviceName', metadata={'description': 'Device name'}
    )
    device_type = fields.String(
        attribute='deviceType',
        metadata={'description': f'Default types: [{", ".join(device_types)}]'},
    )
    remote_type = fields.String(
        attribute='remoteType',
        metadata={'description': f'Default types: [{", ".join(remote_types)}]'},
    )
    hub_id = fields.String(
        attribute='hubDeviceId',
        metadata={'description': 'Parent hub device unique ID'},
    )
    cloud_service_enabled = fields.Boolean(
        attribute='enableCloudService',
        metadata={
            'description': 'True if cloud access is enabled on this device,'
            'False otherwise. Only cloud-enabled devices can be '
            'controlled from the switchbot plugin.'
        },
    )
    is_calibrated = fields.Boolean(
        attribute='calibrate',
        metadata={
            'description': '[Curtain devices only] Set to True if the device '
            'has been calibrated, False otherwise'
        },
    )
    open_direction = fields.String(
        attribute='openDirection',
        metadata={
            'description': '[Curtain devices only] Direction where the curtains '
            'will be opened ("left" or "right")'
        },
    )
    is_virtual = fields.Boolean(
        metadata={
            'description': 'True if this is a virtual device, i.e. a device '
            'with an IR remote configuration but not managed directly by '
            'the Switchbot bridge'
        }
    )


class DeviceStatusSchema(DeviceSchema):
    """
    Schema for SwitchBot devices status.
    """

    on = fields.Boolean(
        attribute='power',
        metadata={'description': 'True if the device is on, False otherwise'},
    )
    voltage = fields.Float(
        allow_none=True,
        metadata={
            'description': '[Plug devices only] Voltage of the device, measured '
            'in volts'
        },
    )
    power = fields.Float(
        attribute='weight',
        allow_none=True,
        metadata={
            'description': '[Plug devices only] Consumed power, measured in watts'
        },
    )
    current = fields.Float(
        attribute='electricCurrent',
        allow_none=True,
        metadata={
            'description': '[Plug devices only] Device current at the moment, '
            'measured in amperes'
        },
    )
    active_time = fields.Int(
        attribute='electricityOfDay',
        allow_none=True,
        metadata={
            'description': '[Plug devices only] How long the device has been '
            'absorbing during a day, measured in minutes'
        },
    )
    moving = fields.Boolean(
        metadata={
            'description': '[Curtain devices only] True if the device is '
            'moving, False otherwise'
        }
    )
    position = fields.Int(
        attribute='slidePosition',
        allow_none=True,
        metadata={
            'description': '[Curtain devices only] Position of the device on '
            'the curtain rail, between 0% (open) and 100% (closed)'
        },
    )
    locked = fields.Boolean(
        attribute='lockState',
        metadata={'description': '[Lock devices only] True if the lock is on'},
    )
    door_open = fields.Boolean(
        attribute='doorState',
        metadata={
            'description': '[Lock devices only] True if the door is open, False otherwise'
        },
    )
    brightness = fields.Int(
        metadata={
            'description': '[Light devices only] Light brightness, between 1 and 100'
        },
        allow_none=True,
        validate=Range(min=1, max=100),
    )
    color = ColorField(
        allow_none=True,
        metadata={
            'description': '[Light devices only] Color, expressed as a hex string (e.g. FF0000)'
        },
    )
    color_temperature = fields.Int(
        attribute='colorTemperature',
        allow_none=True,
        validate=Range(min=2700, max=6500),
        metadata={
            'description': '[Light devices only] Color temperature, between 2700 and 6500'
        },
    )
    temperature = fields.Float(
        allow_none=True,
        metadata={
            'description': '[Meter/humidifier/Air conditioner devices only] '
            'Temperature in Celsius'
        },
    )
    humidity = fields.Float(
        allow_none=True,
        metadata={'description': '[Meter/humidifier devices only] Humidity in %'},
    )
    fan_speed = fields.Int(
        allow_none=True,
        metadata={'description': '[Air conditioner devices only] Speed of the fan'},
    )
    nebulization_efficiency = fields.Float(
        attribute='nebulizationEfficiency',
        allow_none=True,
        metadata={
            'description': '[Humidifier devices only] Nebulization efficiency in %'
        },
    )
    auto = fields.Boolean(
        metadata={'description': '[Humidifier devices only] True if auto mode is on'}
    )
    child_lock = fields.Boolean(
        attribute='childLock',
        metadata={'description': '[Humidifier devices only] True if safety lock is on'},
    )
    sound = fields.Boolean(
        metadata={'description': '[Humidifier devices only] True if sound is muted'}
    )
    low_water = fields.Boolean(
        attribute='lackWater',
        metadata={
            'description': '[Humidifier devices only] True if the device is low on water'
        },
    )
    mode = fields.Int(
        metadata={'description': '[Fan/Air conditioner devices only] Fan mode'}
    )
    speed = fields.Float(
        metadata={'description': '[Smart fan devices only] Fan speed, between 1 and 4'}
    )
    swinging = fields.Boolean(
        attribute='shaking',
        metadata={
            'description': '[Smart fan devices only] True if the device is swinging'
        },
    )
    swing_direction = fields.Int(
        attribute='shakeCenter',
        metadata={'description': '[Smart fan devices only] Swing direction'},
    )
    swing_range = fields.Float(
        attribute='shakeRange',
        metadata={
            'description': '[Smart fan devices only] Swing range angle, between 0 and 120'
        },
    )


class SceneSchema(Schema):
    """
    Schema for SwitchBot scenes.
    """

    id = fields.String(
        attribute='sceneId', required=True, metadata={'description': 'Scene ID'}
    )
    name = fields.String(attribute='sceneName', metadata={'description': 'Scene name'})
