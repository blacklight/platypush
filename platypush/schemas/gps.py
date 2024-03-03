from marshmallow import EXCLUDE, fields, pre_load
from marshmallow.schema import Schema

from platypush.schemas import DateTime


class GpsDeviceSchema(Schema):
    """
    Schema for a GPS device.
    """

    # pylint: disable=too-few-public-methods
    class Meta:  # type: ignore
        """
        Exclude unknown fields from the deserialized output.
        """

        unknown = EXCLUDE

    path = fields.String(
        required=True,
        metadata={
            "description": "Device path",
            "example": "/dev/ttyUSB0",
        },
    )

    activated = DateTime(
        metadata={
            "description": "Device activation status",
            "example": True,
        },
    )

    native = fields.Boolean(
        metadata={
            "description": "Device native status",
            "example": False,
        },
    )

    baudrate = fields.Integer(
        data_key="bps",
        metadata={
            "description": "Device baudrate",
            "example": 9600,
        },
    )

    parity = fields.String(
        metadata={
            "description": "Device parity",
            "example": "N",
        },
    )

    stopbits = fields.Integer(
        metadata={
            "description": "Device stopbits",
            "example": 1,
        },
    )

    cycle = fields.Integer(
        metadata={
            "description": "Device cycle",
            "example": 1,
        },
    )

    driver = fields.String(
        metadata={
            "description": "Device driver",
            "example": "NMEA",
        },
    )

    subtype = fields.String(
        metadata={
            "description": "Device subtype",
            "example": "AXN_2.31_3339_13101700,5632,PA6H,1.0",
        },
    )

    mode = fields.String(
        validate=lambda mode: mode in ["NO_FIX", "TWO_D", "THREE_D"],
        metadata={
            "description": "Device mode, one of NO_FIX, TWO_D, THREE_D",
            "example": "3D",
        },
    )

    @pre_load
    def pre_load(self, data, **_):
        from platypush.plugins.gps import DeviceMode

        if data and data.get("mode"):
            data["mode"] = DeviceMode(data["mode"]).value
        return data


class GpsStatusSchema(Schema):
    """
    Schema for the GPS status.
    """

    latitude = fields.Float(
        metadata={
            "description": "Latitude",
            "example": 45.4642,
        },
    )

    longitude = fields.Float(
        metadata={
            "description": "Longitude",
            "example": 9.1900,
        },
    )

    altitude = fields.Float(
        metadata={
            "description": "Altitude (in meters)",
            "example": 100,
        },
    )

    speed = fields.Float(
        metadata={
            "description": "Measured speed, if available (in km/h)",
            "example": 10,
        },
    )

    satellites_used = fields.Integer(
        metadata={
            "description": "Number of satellites used for the fix",
            "example": 4,
        },
    )

    timestamp = DateTime(
        metadata={
            "description": "Timestamp of the last GPS update",
            "example": "2021-08-01T00:00:00",
        },
    )

    devices = fields.Dict(
        keys=fields.String(),
        values=fields.Nested(GpsDeviceSchema),
        metadata={
            "description": "Available GPS devices",
            "example": {
                "/dev/ttyUSB0": {
                    "path": "/dev/ttyUSB0",
                    "activated": "2021-08-01T00:00:00",
                    "native": False,
                    "baudrate": 9600,
                    "parity": "N",
                    "stopbits": 1,
                    "cycle": 1,
                    "driver": "NMEA",
                    "subtype": "AXN_2.31_3339_13101700,5632,PA6H,1.0",
                    "mode": "3D",
                }
            },
        },
    )
