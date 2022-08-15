from marshmallow import fields
from marshmallow.schema import Schema

from platypush.schemas import DateTime


class MatrixEventIdSchema(Schema):
    event_id = fields.String(
        required=True,
        metadata={
            'description': 'Event ID',
            'example': '$24KT_aQz6sSKaZH8oTCibRTl62qywDgQXMpz5epXsW5',
        },
    )


class MatrixProfileSchema(Schema):
    user_id = fields.String(
        required=True,
        metadata={
            'description': 'User ID',
            'example': '@myuser:matrix.example.org',
        },
    )

    display_name = fields.String(
        attribute='displayname',
        metadata={
            'description': 'User display name',
            'example': 'Foo Bar',
        },
    )

    avatar_url = fields.URL(
        metadata={
            'description': 'User avatar URL',
            'example': 'mxc://matrix.platypush.tech/AbCdEfG0123456789',
        }
    )


class MatrixRoomSchema(Schema):
    room_id = fields.String(
        required=True,
        metadata={
            'description': 'Room ID',
            'example': '!aBcDeFgHiJkMnO:matrix.example.org',
        },
    )

    name = fields.String(
        metadata={
            'description': 'Room name',
            'example': 'My Room',
        }
    )

    display_name = fields.String(
        metadata={
            'description': 'Room display name',
            'example': 'My Room',
        }
    )

    topic = fields.String(
        metadata={
            'description': 'Room topic',
            'example': 'My Room Topic',
        }
    )

    avatar_url = fields.URL(
        attribute='room_avatar_url',
        metadata={
            'description': 'Room avatar URL',
            'example': 'mxc://matrix.platypush.tech/AbCdEfG0123456789',
        },
    )

    owner_id = fields.String(
        attribute='own_user_id',
        metadata={
            'description': 'Owner user ID',
            'example': '@myuser:matrix.example.org',
        },
    )

    encrypted = fields.Bool()


class MatrixDeviceSchema(Schema):
    device_id = fields.String(
        required=True,
        attribute='id',
        metadata={
            'description': 'ABCDEFG',
        },
    )

    display_name = fields.String(
        metadata={
            'description': 'Device display name',
            'example': 'My Device',
        }
    )

    last_seen_ip = fields.String(
        metadata={
            'description': 'Last IP associated to this device',
            'example': '1.2.3.4',
        }
    )

    last_seen_date = DateTime(
        metadata={
            'description': 'The last time that the device was reported online',
            'example': '2022-07-23T17:20:01.254223',
        }
    )
