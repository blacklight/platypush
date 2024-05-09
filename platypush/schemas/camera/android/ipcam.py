from marshmallow import EXCLUDE, fields, pre_dump
from marshmallow.schema import Schema
from marshmallow.validate import OneOf

from platypush.schemas import StrippedString


class CameraStatusSchema(Schema):
    """
    Schema for the camera status.
    """

    class Meta:  # type: ignore
        """
        Exclude unknown fields.
        """

        unknown = EXCLUDE

    name = StrippedString(
        required=True,
        metadata={
            'description': 'Name or IP of the camera',
            'example': 'Front Door',
        },
    )

    stream_url = fields.Url(
        required=True,
        metadata={
            'description': 'URL to the video stream',
            'example': 'http://192.168.1.10:8080/video',
        },
    )

    image_url = fields.Url(
        required=True,
        metadata={
            'description': 'URL to get a snapshot from the camera',
            'example': 'http://192.168.1.10:8080/photo.jpg',
        },
    )

    audio_url = fields.Url(
        required=True,
        metadata={
            'description': 'URL to get audio from the camera',
            'example': 'http://192.168.1.10:8080/audio.wav',
        },
    )

    orientation = fields.Str(
        required=True,
        metadata={
            'description': 'Orientation of the camera',
            'example': 'landscape',
            'validate': OneOf(['landscape', 'portrait']),
        },
    )

    idle = fields.Bool(
        required=True,
        metadata={
            'description': 'Idle status of the camera',
            'example': False,
        },
    )

    audio_only = fields.Bool(
        required=True,
        metadata={
            'description': 'Whether the camera is in audio-only mode',
            'example': False,
        },
    )

    overlay = fields.Bool(
        required=True,
        metadata={
            'description': 'Whether the camera is in overlay mode',
            'example': False,
        },
    )

    quality = fields.Int(
        required=True,
        metadata={
            'description': 'Quality of the video stream, in percent',
            'example': 49,
        },
    )

    night_vision = fields.Bool(
        required=True,
        metadata={
            'description': 'Whether night vision is enabled',
            'example': False,
        },
    )

    night_vision_average = fields.Int(
        required=True,
        metadata={
            'description': 'Average brightness for night vision',
            'example': 2,
        },
    )

    night_vision_gain = fields.Float(
        required=True,
        metadata={
            'description': 'Brightness gain for night vision',
            'example': 1.0,
        },
    )

    ip_address = fields.Str(
        required=True,
        metadata={
            'description': 'IP address of the camera',
            'example': '192.168.1.10',
        },
    )

    motion_limit = fields.Int(
        required=True,
        metadata={
            'description': 'Motion limit',
            'example': 250,
        },
    )

    motion_detect = fields.Bool(
        required=True,
        metadata={
            'description': 'Whether motion detection is enabled',
            'example': False,
        },
    )

    motion_display = fields.Bool(
        required=True,
        metadata={
            'description': 'Whether motion display is enabled',
            'example': False,
        },
    )

    gps_active = fields.Bool(
        required=True,
        metadata={
            'description': 'Whether GPS is active',
            'example': False,
        },
    )

    video_size = fields.Str(
        required=True,
        metadata={
            'description': 'Size of the video stream',
            'example': '1920x1080',
        },
    )

    photo_size = fields.Str(
        required=True,
        metadata={
            'description': 'Size of the photo',
            'example': '1920x1080',
        },
    )

    mirror_flip = fields.Str(
        required=True,
        metadata={
            'description': 'Mirror/flip mode',
            'example': 'none',
            'validate': OneOf(['none', 'horizontal', 'vertical', 'both']),
        },
    )

    video_connections = fields.Int(
        required=True,
        metadata={
            'description': 'Number of active video connections',
            'example': 0,
        },
    )

    audio_connections = fields.Int(
        required=True,
        metadata={
            'description': 'Number of active audio connections',
            'example': 0,
        },
    )

    zoom = fields.Int(
        required=True,
        metadata={
            'description': 'Zoom level, as a percentage',
            'example': 100,
        },
    )

    crop_x = fields.Int(
        required=True,
        metadata={
            'description': 'Crop X, as a percentage',
            'example': 50,
        },
    )

    crop_y = fields.Int(
        required=True,
        metadata={
            'description': 'Crop Y, as a percentage',
            'example': 50,
        },
    )

    coloreffect = fields.Str(
        required=True,
        metadata={
            'description': 'Color effect',
            'example': 'none',
        },
    )

    scenemode = fields.Str(
        required=True,
        metadata={
            'description': 'Scene mode',
            'example': 'auto',
        },
    )

    focusmode = fields.Str(
        required=True,
        metadata={
            'description': 'Focus mode',
            'example': 'continuous-video',
        },
    )

    whitebalance = fields.Str(
        required=True,
        metadata={
            'description': 'White balance',
            'example': 'auto',
        },
    )

    flashmode = fields.Str(
        required=True,
        validate=OneOf(['off', 'on', 'auto']),
        metadata={
            'description': 'Flash mode',
            'example': 'off',
        },
    )

    torch = fields.Bool(
        required=True,
        metadata={
            'description': 'Whether the torch is enabled',
            'example': False,
        },
    )

    focus_distance = fields.Float(
        required=True,
        metadata={
            'description': 'Focus distance',
            'example': 0.0,
        },
    )

    focal_length = fields.Float(
        required=True,
        metadata={
            'description': 'Focal length',
            'example': 4.25,
        },
    )

    aperture = fields.Float(
        required=True,
        metadata={
            'description': 'Aperture',
            'example': 1.7,
        },
    )

    filter_density = fields.Float(
        required=True,
        metadata={
            'description': 'Filter density',
            'example': 0.0,
        },
    )

    exposure_ns = fields.Int(
        required=True,
        metadata={
            'description': 'Exposure time in nanoseconds',
            'example': 9384,
        },
    )

    iso = fields.Int(
        required=True,
        metadata={
            'description': 'ISO',
            'example': 100,
        },
    )

    manual_sensor = fields.Bool(
        required=True,
        metadata={
            'description': 'Whether the sensor is in manual mode',
            'example': False,
        },
    )

    @pre_dump
    def normalize_bools(self, data, **_):
        for k, v in data.items():
            if k != 'flashmode' and isinstance(v, str) and v.lower() in ['on', 'off']:
                data[k] = v.lower() == 'on'
        return data
