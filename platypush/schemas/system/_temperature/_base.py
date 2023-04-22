from marshmallow import pre_load

from .._base import SystemBaseSchema


class TemperatureBaseSchema(SystemBaseSchema):
    """
    Base schema for system temperature sensors.
    """

    @pre_load
    def pre_load(self, data: dict, **_) -> dict:
        data = super().pre_load(data)
        data['value'] = data.pop('current', data.pop('value', None))
        return data
