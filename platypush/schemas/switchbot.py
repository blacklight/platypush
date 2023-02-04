from marshmallow import fields
from marshmallow.schema import Schema


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


class DeviceSchema(Schema):
    """
    Base class for SwitchBot device schemas.
    """

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
    moving = fields.Boolean(
        metadata={
            'description': '[Curtain devices only] True if the device is '
            'moving, False otherwise'
        }
    )
    position = fields.Int(
        attribute='slidePosition',
        metadata={
            'description': '[Curtain devices only] Position of the device on '
            'the curtain rail, between 0 (open) and 1 (closed)'
        },
    )
    temperature = fields.Float(
        metadata={
            'description': '[Meter/humidifier/Air conditioner devices only] '
            'Temperature in Celsius'
        }
    )
    humidity = fields.Float(
        metadata={'description': '[Meter/humidifier devices only] Humidity in %'}
    )
    fan_speed = fields.Int(
        metadata={'description': '[Air conditioner devices only] Speed of the fan'}
    )
    nebulization_efficiency = fields.Float(
        attribute='nebulizationEfficiency',
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
