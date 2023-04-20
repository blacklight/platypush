from marshmallow import pre_load

from platypush.schemas.dataclasses import DataClassSchema


class NetworkInterfaceBaseSchema(DataClassSchema):
    """
    Base schema for network interface stats.
    """

    @pre_load
    def pre_load(self, data: dict, **_) -> dict:
        for in_attr, out_attr in {
            'errin': 'errors_in',
            'errout': 'errors_out',
            'dropin': 'drop_in',
            'dropout': 'drop_out',
        }.items():
            if in_attr in data:
                data[out_attr] = data.pop(in_attr)

        return data
