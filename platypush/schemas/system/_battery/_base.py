from enum import Enum

from marshmallow import pre_load

from .._base import SystemBaseSchema


class BatteryBaseSchema(SystemBaseSchema):
    """
    Base schema for system battery sensors.
    """

    @pre_load
    def pre_load(self, data: dict, **_) -> dict:
        data = super().pre_load(data)
        percent = data.pop('percent', data.pop('value', None))
        seconds_left = data.pop('secsleft', data.pop('seconds_left', None))
        data['value'] = percent / 100 if percent is not None else None
        data['seconds_left'] = None if isinstance(seconds_left, Enum) else seconds_left
        return data
