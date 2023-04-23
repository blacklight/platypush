from datetime import datetime

from dateutil.tz import gettz
from marshmallow import pre_load

from .._base import SystemBaseSchema


class ProcessBaseSchema(SystemBaseSchema):
    """
    Base schema for system processes.
    """

    @pre_load
    def pre_load(self, data, **_) -> dict:
        if hasattr(data, 'as_dict'):
            data = data.as_dict()

        started_ts = data.pop('create_time', None)
        if started_ts is not None:
            data['started'] = datetime.fromtimestamp(started_ts).replace(tzinfo=gettz())

        data['command_line'] = data.pop('cmdline', None)
        data['cpu_percent'] = data.pop('cpu_percent') / 100
        data['current_directory'] = data.pop('cwd', None)
        data['memory_percent'] = data.pop('memory_percent') / 100
        data['parent_pid'] = data.pop('ppid', None)
        return data
