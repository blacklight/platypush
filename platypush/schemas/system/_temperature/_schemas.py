from marshmallow import fields, pre_load

from .._base import SystemBaseSchema


class TemperatureSchema(SystemBaseSchema):
    """
    Schema for system temperature sensors.
    """

    id = fields.String(
        metadata={
            'description': 'The unique identifier of the temperature sensor.',
            'example': 'acpi_1',
        }
    )

    label = fields.String(
        allow_none=True,
        metadata={
            'description': 'The label of the temperature sensor.',
            'example': 'CPU Temperature',
        },
    )

    value = fields.Float(
        allow_none=True,
        metadata={
            'description': 'The current temperature value of the sensor, in degrees Celsius.',
            'example': 56.0,
        },
    )

    high = fields.Float(
        allow_none=True,
        metadata={
            'description': 'The high temperature threshold of the sensor, in degrees Celsius.',
            'example': 90.0,
        },
    )

    critical = fields.Float(
        allow_none=True,
        metadata={
            'description': 'The critical temperature threshold of the sensor, in degrees Celsius.',
            'example': 100.0,
        },
    )

    @pre_load
    def pre_load(self, data: dict, **_) -> dict:
        data = super().pre_load(data)
        data['value'] = data.pop('current', data.pop('value', None))
        return data
