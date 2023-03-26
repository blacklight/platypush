from datetime import date, datetime
from uuid import UUID

from marshmallow import (
    EXCLUDE,
    Schema,
    fields,
    post_dump,
)

from .. import Date, DateTime


class DataClassSchema(Schema):
    """
    Base schema class for data classes that support Marshmallow schemas.
    """

    TYPE_MAPPING = {
        date: Date,
        datetime: DateTime,
        UUID: fields.UUID,
    }

    # pylint: disable=too-few-public-methods
    class Meta:
        """
        Exclude unknown fields.
        """

        unknown = EXCLUDE

    def _get_field(self, key: str) -> fields.Field:
        """
        Returns the matching field by either name or data_key.
        """
        if key in self.fields:
            return self.fields[key]

        matching_fields = [f for f in self.fields.values() if key == f.data_key]

        assert (
            len(matching_fields) == 1
        ), f'Could not find field {key} in {self.__class__.__name__}'

        return matching_fields[0]

    @post_dump
    def post_dump(self, data: dict, **__) -> dict:
        # Use data_key parameters only for load
        new_data = {}
        for key, value in data.items():
            field = self._get_field(key)
            new_data[field.name if field.data_key is not None else key] = value

        return new_data
