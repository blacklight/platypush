from datetime import datetime

from dateutil.tz import gettz
from marshmallow import pre_load

from .._base import SystemBaseSchema


class UserBaseSchema(SystemBaseSchema):
    """
    Base schema for system users.
    """

    @pre_load
    def pre_load(self, data: dict, **_) -> dict:
        data = super().pre_load(data)
        started_ts = data.pop('started', None)
        if started_ts is not None:
            data['started'] = datetime.fromtimestamp(started_ts).replace(tzinfo=gettz())

        data['username'] = data.pop('name', data.pop('username', None))
        return data
