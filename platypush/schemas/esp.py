from marshmallow import EXCLUDE, fields
from marshmallow.schema import Schema


class WifiScanResultSchema(Schema):
    """
    Schema for Wi-Fi scan results.
    """

    class Meta:  # type: ignore
        """
        Exclude unknown fields.
        """

        unknown = EXCLUDE

    essid = fields.Str(
        required=True,
        metadata={
            "description": "ESSID of the Wi-Fi network.",
            "example": "MyNetwork",
        },
    )

    bssid = fields.Str(
        required=True,
        metadata={
            "description": "BSSID of the Wi-Fi network.",
            "example": "00:11:22:33:44:55",
        },
    )

    channel = fields.Int(
        required=True,
        metadata={
            "description": "Channel of the Wi-Fi network.",
            "example": 6,
        },
    )

    rssi = fields.Int(
        required=True,
        metadata={
            "description": "RSSI of the Wi-Fi network.",
            "example": -50,
        },
    )

    auth_mode = fields.Int(
        required=True,
        metadata={
            "description": "Authentication mode of the Wi-Fi network.",
            "example": 3,
        },
    )

    hidden = fields.Bool(
        required=True,
        metadata={
            "description": "Whether the Wi-Fi network is hidden.",
            "example": False,
        },
    )


class WifiConfigSchema(Schema):
    """
    Schema for Wi-Fi configuration.
    """

    class Meta:  # type: ignore
        """
        Exclude unknown fields.
        """

        unknown = EXCLUDE

    ip = fields.Str(
        required=True,
        metadata={
            "description": "IP address of the Wi-Fi interface.",
            "example": "192.168.1.10",
        },
    )

    netmask = fields.Str(
        required=True,
        metadata={
            "description": "Netmask of the Wi-Fi network.",
            "example": "255.255.255.0",
        },
    )

    gateway = fields.Str(
        required=True,
        metadata={
            "description": "Gateway of the Wi-Fi network.",
            "example": "192.168.1.1",
        },
    )

    dns = fields.Str(
        required=True,
        metadata={
            "description": "DNS server of the Wi-Fi network.",
            "example": "1.1.1.1",
        },
    )

    mac = fields.Str(
        required=True,
        metadata={
            "description": "MAC address of the Wi-Fi network.",
            "example": "00:11:22:33:44:55",
        },
    )

    active = fields.Bool(
        required=True,
        metadata={
            "description": "Whether the Wi-Fi network is active.",
            "example": True,
        },
    )

    essid = fields.Str(
        required=True,
        metadata={
            "description": "ESSID of the Wi-Fi network.",
            "example": "MyNetwork",
        },
    )

    channel = fields.Int(
        required=True,
        metadata={
            "description": "Channel of the Wi-Fi network.",
            "example": 6,
        },
    )

    hidden = fields.Bool(
        required=True,
        metadata={
            "description": "Whether the Wi-Fi network is hidden.",
            "example": False,
        },
    )
