from marshmallow import pre_load

from platypush.schemas.dataclasses import DataClassSchema


class ConnectionBaseSchema(DataClassSchema):
    """
    Base schema for connections.
    """

    @pre_load
    def pre_load(self, data, **_) -> dict:
        if hasattr(data, '_asdict'):
            data = data._asdict()

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
