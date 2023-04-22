from marshmallow import pre_load

from .._base import SystemBaseSchema


class MemoryStatsBaseSchema(SystemBaseSchema):
    """
    Base schema for memory stats.
    """

    @pre_load
    def pre_load(self, data: dict, **_) -> dict:
        data = super().pre_load(data)

        # Normalize the percentage between 0 and 1
        if data.get('percent') is not None:
            data['percent'] /= 100
        return data
