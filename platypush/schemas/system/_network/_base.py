from enum import Enum
from socket import AddressFamily

from marshmallow import pre_load

from .._base import SystemBaseSchema


class NetworkInterfaceBaseSchema(SystemBaseSchema):
    """
    Base schema for network interface stats.
    """

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
