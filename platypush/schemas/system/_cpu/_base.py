from marshmallow import pre_load

from platypush.schemas.dataclasses import DataClassSchema


class CpuInfoBaseSchema(DataClassSchema):
    """
    Base schema for CPU info.
    """

    @pre_load
    def pre_load(self, data: dict, **_) -> dict:
        if data.get('hz_advertised'):
            data['frequency_advertised'] = data.pop('hz_advertised')[0]
        if data.get('hz_actual'):
            data['frequency_actual'] = data.pop('hz_actual')[0]

        return data


class CpuTimesBaseSchema(DataClassSchema):
    """
    Base schema for CPU times.
    """

    @pre_load
    def pre_load(self, data, **_) -> dict:
        """
        Convert the underlying object to dict and normalize all the percentage
        values from [0, 100] to [0, 1].
        """
        return {
            key: value / 100.0
            for key, value in (
                data if isinstance(data, dict) else data._asdict()
            ).items()
        }
