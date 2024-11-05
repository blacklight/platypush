from marshmallow import fields, pre_load

from platypush.schemas.dataclasses import percent_field
from .._base import SystemBaseSchema


class DiskSchema(SystemBaseSchema):
    """
    Base schema for disk stats.
    """

    device = fields.String(
        required=True,
        metadata={
            'description': 'Path/identifier of the disk/partition',
            'example': '/dev/sda1',
        },
    )

    mountpoint = fields.String(
        metadata={
            'description': 'Mountpoint of the disk/partition',
            'example': '/mnt/data',
        }
    )

    fstype = fields.String(
        metadata={
            'description': 'Filesystem type',
            'example': 'ext4',
        }
    )

    opts = fields.String(  # type: ignore
        metadata={
            'description': 'Mount options',
            'example': 'rw,relatime',
        }
    )

    total = fields.Integer(
        metadata={
            'description': 'Total disk space in bytes',
            'example': 1024**3,
        }
    )

    used = fields.Integer(
        metadata={
            'description': 'Used disk space in bytes',
            'example': 1024**2,
        }
    )

    free = fields.Integer(
        metadata={
            'description': 'Free disk space in bytes',
            'example': (1024**3) - (1024**2),
        }
    )

    read_count = fields.Integer(
        metadata={
            'description': 'Number of read operations',
            'example': 100,
        }
    )

    write_count = fields.Integer(
        metadata={
            'description': 'Number of write operations',
            'example': 50,
        }
    )

    read_bytes = fields.Integer(
        metadata={
            'description': 'Number of bytes read',
            'example': 1024**3,
        }
    )

    write_bytes = fields.Integer(
        metadata={
            'description': 'Number of bytes written',
            'example': 1024**2,
        }
    )

    read_time = fields.Float(
        metadata={
            'description': 'Time spent reading in seconds',
            'example': 10.5,
        }
    )

    write_time = fields.Float(
        metadata={
            'description': 'Time spent writing in seconds',
            'example': 5.5,
        }
    )

    busy_time = fields.Float(
        metadata={
            'description': 'Time spent doing I/Os in seconds',
            'example': 20.5,
        }
    )

    percent = percent_field(
        metadata={
            'description': 'Percentage of disk space used, normalized between 0 and 1',
            'example': 0.1,
        }
    )

    @pre_load
    def pre_load(self, data: dict, **_) -> dict:
        data = super().pre_load(data)

        # Convert read/write/busy times from milliseconds to seconds
        for attr in ['read_time', 'write_time', 'busy_time']:
            if data.get(attr) is not None:
                data[attr] /= 1000

        # Normalize the percentage between 0 and 1
        if data.get('percent') is not None:
            data['percent'] /= 100

        return data
