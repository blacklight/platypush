from datetime import datetime

from dateutil.tz import gettz
from marshmallow import fields, pre_load

from platypush.schemas import DateTime
from platypush.schemas.dataclasses import percent_field
from .._base import SystemBaseSchema


class ProcessSchema(SystemBaseSchema):
    """
    Schema for system processes.
    """

    pid = fields.Int(
        missing=-1,
        metadata={
            'description': 'The process ID.',
            'example': 1234,
        },
    )

    name = fields.String(
        allow_none=True,
        metadata={
            'description': 'The name of the process.',
            'example': 'python',
        },
    )

    parent_pid = fields.Int(
        allow_none=True,
        metadata={
            'description': 'The parent process ID.',
            'example': 1000,
        },
    )

    username = fields.String(
        allow_none=True,
        metadata={
            'description': 'The username of the process owner.',
            'example': 'root',
        },
    )

    command_line = fields.List(
        fields.String(),
        allow_none=True,
        metadata={
            'description': 'The command line arguments of the process.',
            'example': ['python', 'script.py'],
        },
    )

    status = fields.String(
        allow_none=True,
        metadata={
            'description': 'The status of the process.',
            'example': 'running',
        },
    )

    terminal = fields.String(
        allow_none=True,
        metadata={
            'description': 'The terminal of the process.',
            'example': 'tty1',
        },
    )

    current_directory = fields.String(
        allow_none=True,
        metadata={
            'description': 'The current working directory of the process.',
            'example': '/home/user',
        },
    )

    started = DateTime(
        allow_none=True,
        metadata={
            'description': 'The timestamp when the process was started.',
            'example': '2021-01-01T00:00:00+00:00',
        },
    )

    cpu_percent = percent_field(
        missing=0,
        metadata={
            'description': 'The CPU usage percentage of the process, in the range [0, 1].',
            'example': 0.5,
        },
    )

    memory_percent = percent_field(
        missing=0,
        metadata={
            'description': 'The memory usage percentage of the process, in the range [0, 1].',
            'example': 0.5,
        },
    )

    @pre_load
    def pre_load(self, data, **_) -> dict:
        import psutil

        if hasattr(data, 'as_dict'):
            try:
                data = data.as_dict()
            except psutil.NoSuchProcess:
                return {}

        started_ts = data.pop('create_time', None)
        if started_ts is not None:
            data['started'] = datetime.fromtimestamp(started_ts).replace(tzinfo=gettz())

        data['command_line'] = data.pop('cmdline', None)
        data['cpu_percent'] = data.pop('cpu_percent') / 100
        data['current_directory'] = data.pop('cwd', None)
        data['memory_percent'] = data.pop('memory_percent') / 100
        data['parent_pid'] = data.pop('ppid', None)
        return data
