import os

from marshmallow import fields
from marshmallow.schema import Schema

from platypush.schemas import StrippedString


class IRCServerSchema(Schema):
    server = fields.String(
        required=True,
        metadata=dict(
            description='Server address or hostname',
            example='irc.example.org',
        )
    )

    port = fields.Int(
        missing=6667,
        metadata=dict(
            description='IRC server port',
            example=6667,
        )
    )

    password = fields.String(allow_none=True, default=None, metadata=dict(example='password'))
    nickname = fields.String(required=True, metadata=dict(example='testbot'))
    realname = fields.String(allow_none=True, metadata=dict(example='My Real Name'))
    alias = StrippedString(
        metadata=dict(description='Friendly name for this bot/server connection')
    )

    channels = fields.List(
        fields.String(),
        missing=list,
        metadata=dict(
            description='List of channels the bot will connect to',
            example=['#channel1', '#channel2', '#channel3']
        )
    )

    ssl = fields.Boolean(missing=False)
    ipv6 = fields.Boolean(missing=False)
    stop_message = StrippedString(missing='Application stopped', metadata=dict(description='Quit/die message'))

    dcc_ip_whitelist = fields.List(
        fields.String,
        missing=list,
        metadata=dict(
            description='If specified then only DCC connections from the IP addresses on this list will be accepted',
        )
    )

    dcc_ip_blacklist = fields.List(
        fields.String,
        missing=list,
        metadata=dict(
            description='If specified then DCC connections from the IP addresses on this list will be rejected',
        )
    )

    dcc_nick_whitelist = fields.List(
        fields.String,
        missing=list,
        metadata=dict(
            description='If specified then only DCC connections from the nicknames on this list will be accepted',
        )
    )

    dcc_nick_blacklist = fields.List(
        fields.String,
        missing=list,
        metadata=dict(
            description='If specified then DCC connections from the nicknames on this list will be rejected',
        )
    )

    dcc_downloads_dir = fields.String(
        missing=os.path.join(os.path.expanduser('~'), 'Downloads'),
        metadata=dict(description='DCC file transfers will be downloaded to this folder (default: ~/Downloads)'),
    )

    response_timeout = fields.Number(
        missing=30.,
        metadata=dict(
            description='How long we should wait for a response to an IRC request '
                        '(default: 30 seconds)',
        )
    )

    dcc_file_transfer_timeout = fields.Number(
        missing=30.,
        metadata=dict(
            description='How long we should wait on a pending DCC file transfer with '
                        'no data being transmitted (default: 30 seconds)',
        )
    )

    dcc_accept_timeout = fields.Number(
        missing=300.,
        metadata=dict(
            description='How long we should wait on a pending DCC request '
                        'until the user accepts (default: 300 seconds)',
        )
    )

    dcc_max_connections = fields.Int(
        missing=10,
        metadata=dict(
            description='Maximum number of concurrent DCC connections allowed on this bot (default: 10)'
        )
    )


class IRCServerStatusSchema(Schema):
    server = StrippedString(required=True)
    port = fields.Int(required=True)
    alias = StrippedString()
    real_name = fields.String()
    nickname = fields.String()
    is_connected = fields.Boolean()
    connected_channels = fields.List(fields.String)


class IRCChannelSchema(Schema):
    name = fields.String(required=True)
    modes = fields.List(fields.String)
    opers = fields.List(fields.String)
    owners = fields.List(fields.String)
    users = fields.List(fields.String)
    voiced = fields.List(fields.String)
    is_invite_only = fields.Boolean()
    is_moderated = fields.Boolean()
    is_protected = fields.Boolean()
    is_secret = fields.Boolean()
