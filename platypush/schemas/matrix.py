from marshmallow import fields
from marshmallow.schema import Schema

from platypush.schemas import DateTime


class MillisecondsTimestamp(DateTime):
    def _get_attr(self, *args, **kwargs):
        value = super()._get_attr(*args, **kwargs)
        if isinstance(value, int):
            value = float(value / 1000)
        return value


class MatrixEventIdSchema(Schema):
    event_id = fields.String(
        required=True,
        metadata={
            'description': 'Event ID',
            'example': '$24KT_aQz6sSKaZH8oTCibRTl62qywDgQXMpz5epXsW5',
        },
    )


class MatrixRoomIdSchema(Schema):
    room_id = fields.String(
        required=True,
        metadata={
            'description': 'Room ID',
            'example': '!aBcDeFgHiJkMnO:matrix.example.org',
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
            'example': 'mxc://matrix.example.org/AbCdEfG0123456789',
        }
    )


class MatrixMemberSchema(MatrixProfileSchema):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['display_name'].attribute = 'display_name'


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
            'example': 'mxc://matrix.example.org/AbCdEfG0123456789',
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

    user_id = fields.String(
        required=True,
        metadata={
            'description': 'User ID associated to the device',
            'example': '@myuser:matrix.example.org',
        },
    )

    display_name = fields.String(
        metadata={
            'description': 'Display name of the device',
            'example': 'Element Android',
        },
    )

    blacklisted = fields.Boolean()
    deleted = fields.Boolean(default=False)
    ignored = fields.Boolean()
    verified = fields.Boolean()

    keys = fields.Dict(
        metadata={
            'description': 'Encryption keys supported by the device',
            'example': {
                'curve25519': 'BtlB0vaQmtYFsvOYkmxyzw9qP5yGjuAyRh4gXh3q',
                'ed25519': 'atohIK2FeVlYoY8xxpZ1bhDbveD+HA2DswNFqUxP',
            },
        },
    )


class MatrixMyDeviceSchema(Schema):
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


class MatrixDownloadedFileSchema(Schema):
    url = fields.String(
        metadata={
            'description': 'Matrix URL of the original resource',
            'example': 'mxc://matrix.example.org/YhQycHvFOvtiDDbEeWWtEhXx',
        },
    )

    path = fields.String(
        metadata={
            'description': 'Local path where the file has been saved',
            'example': '/home/user/Downloads/image.png',
        }
    )

    content_type = fields.String(
        metadata={
            'description': 'Content type of the downloaded file',
            'example': 'image/png',
        }
    )

    size = fields.Int(
        metadata={
            'description': 'Length in bytes of the output file',
            'example': 1024,
        }
    )


class MatrixMessageSchema(Schema):
    event_id = fields.String(
        required=True,
        metadata={
            'description': 'Event ID associated to this message',
            'example': '$2eOQ5ueafANj91GnPCRkRUOOjM7dI5kFDOlfMNCD2ly',
        },
    )

    room_id = fields.String(
        required=True,
        metadata={
            'description': 'The ID of the room containing the message',
            'example': '!aBcDeFgHiJkMnO:matrix.example.org',
        },
    )

    user_id = fields.String(
        required=True,
        attribute='sender',
        metadata={
            'description': 'ID of the user who sent the message',
            'example': '@myuser:matrix.example.org',
        },
    )

    body = fields.String(
        required=True,
        metadata={
            'description': 'Message body',
            'example': 'Hello world!',
        },
    )

    format = fields.String(
        metadata={
            'description': 'Message format',
            'example': 'markdown',
        },
    )

    formatted_body = fields.String(
        metadata={
            'description': 'Formatted body',
            'example': '**Hello world!**',
        },
    )

    url = fields.String(
        metadata={
            'description': 'mxc:// URL if this message contains an attachment',
            'example': 'mxc://matrix.example.org/oarGdlpvcwppARPjzNlmlXkD',
        },
    )

    content_type = fields.String(
        attribute='mimetype',
        metadata={
            'description': 'If the message contains an attachment, this field '
            'will contain its MIME type',
            'example': 'image/jpeg',
        },
    )

    transaction_id = fields.String(
        metadata={
            'description': 'Set if this message a unique transaction_id associated',
            'example': 'mQ8hZR6Dx8I8YDMwONYmBkf7lTgJSMV/ZPqosDNM',
        },
    )

    decrypted = fields.Bool(
        metadata={
            'description': 'True if the message was encrypted and has been '
            'successfully decrypted',
        },
    )

    verified = fields.Bool(
        metadata={
            'description': 'True if this is an encrypted message coming from a '
            'verified source'
        },
    )

    hashes = fields.Dict(
        metadata={
            'description': 'If the message has been decrypted, this field '
            'contains a mapping of its hashes',
            'example': {'sha256': 'yoQLQwcURq6/bJp1xQ/uhn9Z2xeA27KhMhPd/mfT8tR'},
        },
    )

    iv = fields.String(
        metadata={
            'description': 'If the message has been decrypted, this field '
            'contains the encryption initial value',
            'example': 'NqJMMdijlLvAAAAAAAAAAA',
        },
    )

    key = fields.Dict(
        metadata={
            'description': 'If the message has been decrypted, this field '
            'contains the encryption/decryption key',
            'example': {
                'alg': 'A256CTR',
                'ext': True,
                'k': 'u6jjAyNvJoBHE55P5ZfvX49m3oSt9s_L4PSQdprRSJI',
                'key_ops': ['encrypt', 'decrypt'],
                'kty': 'oct',
            },
        },
    )

    timestamp = MillisecondsTimestamp(
        required=True,
        attribute='server_timestamp',
        metadata={
            'description': 'When the event was registered on the server',
            'example': '2022-07-23T17:20:01.254223',
        },
    )


class MatrixMessagesResponseSchema(Schema):
    messages = fields.Nested(
        MatrixMessageSchema,
        many=True,
        required=True,
        attribute='chunk',
    )

    start = fields.String(
        required=True,
        nullable=True,
        metadata={
            'description': 'Pointer to the first message. It can be used as a '
            '``start``/``end`` for another ``get_messages`` query.',
            'example': 's10226_143893_619_3648_5951_5_555_7501_0',
        },
    )

    end = fields.String(
        required=True,
        nullable=True,
        metadata={
            'description': 'Pointer to the last message. It can be used as a '
            '``start``/``end`` for another ``get_messages`` query.',
            'example': 't2-10202_143892_626_3663_5949_6_558_7501_0',
        },
    )

    start_time = MillisecondsTimestamp(
        required=True,
        nullable=True,
        metadata={
            'description': 'The oldest timestamp of the returned messages',
            'example': '2022-07-23T16:20:01.254223',
        },
    )

    end_time = MillisecondsTimestamp(
        required=True,
        nullable=True,
        metadata={
            'description': 'The newest timestamp of the returned messages',
            'example': '2022-07-23T18:20:01.254223',
        },
    )
