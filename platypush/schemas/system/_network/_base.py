from marshmallow import pre_load

from .._base import SystemBaseSchema


class NetworkInterfaceBaseSchema(SystemBaseSchema):
    """
    Base schema for network interface stats.
    """

    @pre_load
    def pre_load(self, data: dict, **_) -> dict:
        data = super().pre_load(data)
        for in_attr, out_attr in {
            'errin': 'errors_in',
            'errout': 'errors_out',
            'dropin': 'drop_in',
            'dropout': 'drop_out',
        }.items():
            if in_attr in data:
                data[out_attr] = data.pop(in_attr)

        return data
