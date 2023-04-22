from marshmallow import pre_load

from platypush.schemas.dataclasses import DataClassSchema


class SystemBaseSchema(DataClassSchema):
    """
    Base schema for system info.
    """

    @pre_load
    def pre_load(self, data, **_) -> dict:
        if hasattr(data, '_asdict'):
            data = data._asdict()
        return data
