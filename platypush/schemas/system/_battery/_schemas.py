from enum import Enum

from marshmallow import fields, pre_load

from platypush.schemas.dataclasses import percent_field

from .._base import SystemBaseSchema


class BatterySchema(SystemBaseSchema):
    """
    System battery sensor schema.
    """

    seconds_left = fields.Float(
        allow_none=True,
        metadata={
            'description': 'Number of seconds left before the battery runs out',
            'example': 7200,
        },
    )

    power_plugged = fields.Boolean(
        metadata={
            'description': 'Whether the battery is currently plugged in',
            'example': False,
        }
    )

    value = percent_field(
        allow_none=True,
        metadata={
            'description': 'Current battery charge level, as a percentage between 0 and 1',
            'example': 0.5,
        },
    )

    @pre_load
    def pre_load(self, data: dict, **_) -> dict:
        data = super().pre_load(data)
        percent = data.pop('percent', data.pop('value', None))
        seconds_left = data.pop('secsleft', data.pop('seconds_left', None))
        data['value'] = percent / 100 if percent is not None else None
        data['seconds_left'] = None if isinstance(seconds_left, Enum) else seconds_left
        return data
