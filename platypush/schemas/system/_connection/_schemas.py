from marshmallow import fields, pre_load

from .._base import SystemBaseSchema


class ConnectionSchema(SystemBaseSchema):
    """
    Base schema for connections.
    """

    fd = fields.Int(
        required=True,
        metadata={
            'description': 'File descriptor number.',
            'example': 3,
        },
    )

    family = fields.String(
        allow_none=True,
        metadata={
            'description': 'Address family.',
            'example': 'AF_INET',
        },
    )

    type = fields.String(
        allow_none=True,
        metadata={
            'description': 'Socket type.',
            'example': 'SOCK_STREAM',
        },
    )

    local_address = fields.String(
        allow_none=True,
        metadata={
            'description': 'Local address.',
            'example': '192.168.1.3',
        },
    )

    local_port = fields.Int(
        allow_none=True,
        metadata={
            'description': 'Local port.',
            'example': 1234,
        },
    )

    remote_address = fields.String(
        allow_none=True,
        metadata={
            'description': 'Remote address.',
            'example': '192.168.1.4',
        },
    )

    remote_port = fields.Int(
        allow_none=True,
        metadata={
            'description': 'Remote port.',
            'example': 5678,
        },
    )

    status = fields.String(
        allow_none=True,
        metadata={
            'description': 'Connection status.',
            'example': 'ESTABLISHED',
        },
    )

    pid = fields.Int(
        allow_none=True,
        metadata={
            'description': 'ID of the process that owns the connection.',
            'example': 1234,
        },
    )

    @pre_load
    def pre_load(self, data, **_) -> dict:
        data = super().pre_load(data)
        addr_mapping = {
            'laddr': ('local_address', 'local_port'),
            'raddr': ('remote_address', 'remote_port'),
        }

        # Parse laddr/raddr attributes
        for ext_attr, (addr_attr, port_attr) in addr_mapping.items():
            value = data.pop(ext_attr, None)
            if not value:
                data[addr_attr] = data[port_attr] = None
            elif isinstance(value, tuple):
                data[addr_attr], data[port_attr] = value
            elif isinstance(value, str):
                data[addr_attr] = value
                data[port_attr] = None

        # Handle enum values
        for attr in ['type', 'family']:
            value = data.pop(attr, None)
            if value is not None:
                data[attr] = value.name

        if data.get('status') == 'NONE':
            data['status'] = None

        return data
