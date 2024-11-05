from datetime import datetime

from dateutil.tz import gettz
from marshmallow import fields, pre_load

from platypush.schemas import DateTime

from .._base import SystemBaseSchema


class UserSchema(SystemBaseSchema):
    """
    Schema for system users.
    """

    username = fields.String(
        required=True,
        metadata={'description': 'The username of the user.', 'example': 'johndoe'},
    )

    terminal = fields.String(
        metadata={
            'description': 'The terminal the user is currently using.',
            'example': 'tty1',
        }
    )

    started = DateTime(
        metadata={
            'description': 'The timestamp when the user session started.',
            'example': '2021-01-01T00:00:00+00:00',
        }
    )

    pid = fields.Integer(
        metadata={'description': 'The PID of the user session.', 'example': 1234}
    )

    @pre_load
    def pre_load(self, data: dict, **_) -> dict:
        data = super().pre_load(data)
        started_ts = data.pop('started', None)
        if started_ts is not None:
            data['started'] = datetime.fromtimestamp(started_ts).replace(tzinfo=gettz())

        data['username'] = data.pop('name', data.pop('username', None))
        return data
