from marshmallow import fields
from marshmallow.schema import Schema
from marshmallow.validate import OneOf


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
    'Others',
]


class DeviceSchema(Schema):
    id = fields.String(attribute='deviceId', required=True, metadata=dict(description='Device unique ID'))
    name = fields.String(attribute='deviceName', metadata=dict(description='Device name'))
    type = fields.String(attribute='deviceType', required=True, validate=OneOf(device_types),
                         metadata=dict(description=f'Supported types: [{", ".join(device_types)}]'))
    hub_id = fields.String(attribute='hubDeviceId', metadata=dict(description='Parent hub device unique ID'))
    cloud_service_enabled = fields.Boolean(attribute='enableCloudService',
                                           metadata=dict(description='True if cloud access is enabled on this device,'
                                                         'False otherwise. Only cloud-enabled devices can be '
                                                         'controlled from the switchbot plugin.'))
    calibrated = fields.Boolean(attribute='calibrate',
                                metadata=dict(description='[Curtain devices only] Set to True if the device has '
                                              'been calibrated, False otherwise'))
    open_direction = fields.String(attribute='openDirection',
                                   metadata=dict(description='[Curtain devices only] Direction where the curtains will '
                                                             'be opened ("left" or "right")'))


class DeviceStatusSchema(DeviceSchema):
    on = fields.Boolean(attribute='power', metadata=dict(description='True if the device is on, False otherwise'))
    moving = fields.Boolean(metadata=dict(
        description='[Curtain devices only] True if the device is moving, False otherwise'))
    position = fields.Int(attribute='slidePosition', metadata=dict(
        description='[Curtain devices only] Position of the device on the curtain rail, between '
                    '0 (open) and 1 (closed)'))
    temperature = fields.Float(metadata=dict(description='[Meter/humidifier devices only] Temperature in Celsius'))
    humidity = fields.Float(metadata=dict(description='[Meter/humidifier devices only] Humidity in %'))
    nebulization_efficiency = fields.Float(attribute='nebulizationEfficiency',
                                           metadata=dict(description='[Humidifier devices only] Nebulization '
                                                                     'efficiency in %'))
    auto = fields.Boolean(metadata=dict(description='[Humidifier devices only] True if auto mode is on'))
    child_lock = fields.Boolean(attribute='childLock',
                                metadata=dict(description='[Humidifier devices only] True if safety lock is on'))
    sound = fields.Boolean(metadata=dict(description='[Humidifier devices only] True if sound is muted'))
    mode = fields.Int(metadata=dict(description='[Smart fan devices only] Fan mode'))
    speed = fields.Float(metadata=dict(description='[Smart fan devices only] Fan speed, between 1 and 4'))
    swinging = fields.Boolean(attribute='shaking',
                              metadata=dict(description='[Smart fan devices only] True if the device is swinging'))
    swing_direction = fields.Int(attribute='shakeCenter',
                                 metadata=dict(description='[Smart fan devices only] Swing direction'))
    swing_range = fields.Float(attribute='shakeRange',
                               metadata=dict(description='[Smart fan devices only] Swing range angle, '
                                                         'between 0 and 120'))


class SceneSchema(Schema):
    id = fields.String(attribute='sceneId', required=True, metadata=dict(description='Scene ID'))
    name = fields.String(attribute='sceneName', metadata=dict(description='Scene name'))
