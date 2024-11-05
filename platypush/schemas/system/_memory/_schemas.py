from marshmallow import fields, pre_load

from platypush.schemas.dataclasses import percent_field

from .._base import SystemBaseSchema


class MemoryStatsSchema(SystemBaseSchema):
    """
    Base schema for memory stats.
    """

    total = fields.Integer(
        metadata={
            'description': 'Total memory available in bytes.',
            'example': 8589934592,
        }
    )

    available = fields.Integer(
        metadata={
            'description': 'Memory available in bytes.',
            'example': 2147483648,
        }
    )

    used = fields.Integer(
        metadata={
            'description': 'Memory used in bytes.',
            'example': 6442450944,
        }
    )

    free = fields.Integer(
        metadata={
            'description': 'Memory free in bytes.',
            'example': 2147483648,
        }
    )

    active = fields.Integer(
        metadata={
            'description': 'Memory active in bytes.',
            'example': 4294967296,
        }
    )

    inactive = fields.Integer(
        metadata={
            'description': 'Memory inactive in bytes.',
            'example': 2147483648,
        }
    )

    buffers = fields.Integer(
        metadata={
            'description': 'Memory buffers in bytes.',
            'example': 2147483648,
        }
    )

    cached = fields.Integer(
        metadata={
            'description': 'Memory cached in bytes.',
            'example': 2147483648,
        }
    )

    shared = fields.Integer(
        metadata={
            'description': 'Memory shared in bytes.',
            'example': 3221225472,
        }
    )

    percent = percent_field(
        metadata={
            'description': 'Memory usage percentage between 0 and 1.',
            'example': 0.75,
        }
    )

    @pre_load
    def pre_load(self, data: dict, **_) -> dict:
        data = super().pre_load(data)

        # Normalize the percentage between 0 and 1
        if data.get('percent') is not None:
            data['percent'] /= 100
        return data


class SwapStatsSchema(SystemBaseSchema):
    """
    Base schema for swap stats.
    """

    total = fields.Integer(
        metadata={
            'description': 'Total memory available in bytes.',
            'example': 8589934592,
        }
    )

    used = fields.Integer(
        metadata={
            'description': 'Memory used in bytes.',
            'example': 6442450944,
        }
    )

    free = fields.Integer(
        metadata={
            'description': 'Memory free in bytes.',
            'example': 2147483648,
        }
    )

    percent = percent_field(
        metadata={
            'description': 'Memory usage percentage between 0 and 1.',
            'example': 0.75,
        }
    )

    @pre_load
    def pre_load(self, data: dict, **_) -> dict:
        data = super().pre_load(data)

        # Normalize the percentage between 0 and 1
        if data.get('percent') is not None:
            data['percent'] /= 100
        return data
