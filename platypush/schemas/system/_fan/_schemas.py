from marshmallow import fields, pre_load

from .._base import SystemBaseSchema


class FanSchema(SystemBaseSchema):
    """
    Base schema for system fan sensors.
    """

    id = fields.String(
        required=True,
        metadata={
            'description': 'Unique ID for the sensor',
            'example': 'acpi_1',
        },
    )

    label = fields.String(
        allow_none=True,
        metadata={
            'description': 'Label for the sensor',
            'example': 'CPU Fan',
        },
    )

    value = fields.Float(
        allow_none=True,
        metadata={
            'description': 'Current fan speed in RPM',
            'example': 1200,
        },
    )

    @pre_load
    def pre_load(self, data: dict, **_) -> dict:
        data = super().pre_load(data)
        data['value'] = data.pop('current', data.pop('value', None))
        return data
