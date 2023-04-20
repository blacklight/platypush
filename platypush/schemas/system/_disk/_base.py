from marshmallow import pre_load

from platypush.schemas.dataclasses import DataClassSchema


class DiskBaseSchema(DataClassSchema):
    """
    Base schema for disk stats.
    """

    @pre_load
    def pre_load(self, data: dict, **_) -> dict:
        # Convert read/write/busy times from milliseconds to seconds
        for attr in ['read_time', 'write_time', 'busy_time']:
            if data.get(attr) is not None:
                data[attr] /= 1000

        # Normalize the percentage between 0 and 1
        if data.get('percent') is not None:
            data['percent'] /= 100

        return data
