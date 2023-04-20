from marshmallow import pre_load

from platypush.schemas.dataclasses import DataClassSchema


class MemoryStatsBaseSchema(DataClassSchema):
    """
    Base schema for memory stats.
    """

    @pre_load
    def pre_load(self, data: dict, **_) -> dict:
        # Normalize the percentage between 0 and 1
        if data.get('percent') is not None:
            data['percent'] /= 100
        return data
