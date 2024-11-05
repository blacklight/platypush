from enum import Enum
from socket import AddressFamily

from marshmallow import fields, pre_load
from marshmallow.validate import OneOf

from .._base import SystemBaseSchema


class NetworkInterfaceAddressSchema(SystemBaseSchema):
    """
    Schema for network interface address.
    """

    family = fields.String(
        allow_none=True,
        metadata={
            'description': 'The address family.',
            'example': 'AF_INET',
        },
    )

    address = fields.String(
        allow_none=True,
        metadata={
            'description': 'The IP address associated with the interface.',
            'example': '192.168.1.4',
        },
    )

    netmask = fields.String(
        allow_none=True,
        metadata={
            'description': 'The netmask associated with the interface.',
            'example': '255.255.255.0',
        },
    )

    broadcast = fields.String(
        allow_none=True,
        metadata={
            'description': 'The broadcast address associated with the interface.',
            'example': '192.168.1.255',
        },
    )


class NetworkInterfaceSchema(SystemBaseSchema):
    """
    Schema for network interface stats.
    """

    interface = fields.String(
        allow_none=True,
        metadata={
            'description': 'The name of the network interface.',
            'example': 'eth0',
        },
    )

    bytes_sent = fields.Integer(
        missing=0,
        metadata={
            'description': 'The number of bytes sent.',
            'example': 123456,
        },
    )

    bytes_recv = fields.Integer(
        missing=0,
        metadata={
            'description': 'The number of bytes received.',
            'example': 654321,
        },
    )

    packets_sent = fields.Integer(
        missing=0,
        metadata={
            'description': 'The number of packets sent.',
            'example': 123,
        },
    )

    packets_recv = fields.Integer(
        missing=0,
        metadata={
            'description': 'The number of packets received.',
            'example': 321,
        },
    )

    errors_in = fields.Integer(
        missing=0,
        metadata={
            'description': 'The number of errors on the input side.',
            'example': 10,
        },
    )

    errors_out = fields.Integer(
        missing=0,
        metadata={
            'description': 'The number of errors on the output side.',
            'example': 5,
        },
    )

    drop_in = fields.Integer(
        missing=0,
        metadata={
            'description': 'The number of dropped packets on the input side.',
            'example': 1,
        },
    )

    drop_out = fields.Integer(
        missing=0,
        metadata={
            'description': 'The number of dropped packets on the output side.',
            'example': 2,
        },
    )

    is_up = fields.Boolean(
        metadata={
            'description': 'Whether the interface is up.',
            'example': True,
        },
    )

    speed = fields.Integer(
        metadata={
            'description': 'The advertised speed of the interface in Mbps.',
            'example': 1000,
        },
    )

    mtu = fields.Integer(
        metadata={
            'description': 'The maximum transmission unit of the interface in bytes.',
            'example': 1500,
        },
    )

    duplex = fields.String(
        validate=OneOf(['FULL', 'HALF', 'UNKNOWN']),
        metadata={
            'description': 'Interface duplex configuration. Can be FULL, '
            'HALF or UNKNOWN',
            'example': 'FULL',
        },
    )

    flags = fields.List(
        fields.String(),
        metadata={
            'description': 'A list of flags associated with the interface.',
            'example': ['up', 'broadcast', 'running', 'multicast'],
        },
    )

    addresses = fields.List(
        fields.Nested(NetworkInterfaceAddressSchema),
        metadata={
            'description': 'A list of addresses associated with the interface.',
            'example': [
                {
                    'family': 'AF_INET',
                    'address': '192.168.1.4',
                    'netmask': '255.255.255.0',
                    'broadcast': '192.168.1.255',
                },
            ],
        },
    )

    @pre_load
    def pre_load(self, data: dict, **_) -> dict:
        data = super().pre_load(data)

        # Custom attribute mappings
        for in_attr, out_attr in {
            'errin': 'errors_in',
            'errout': 'errors_out',
            'dropin': 'drop_in',
            'dropout': 'drop_out',
            'isup': 'is_up',
        }.items():
            if in_attr in data:
                data[out_attr] = data.pop(in_attr)

        # Serialize enum values
        for i, addr in enumerate(data.get('addresses', [])):
            if hasattr(addr, '_asdict'):
                addr = addr._asdict()
            if isinstance(addr.get('family'), AddressFamily):
                addr['family'] = addr['family'].name
            data['addresses'][i] = addr

        if isinstance(data.get('duplex'), Enum):
            data['duplex'] = data['duplex'].name.split('_')[-1]

        # Split the flags string
        data['flags'] = data.get('flags', '').split(',')

        return data
