from typing import Any, Optional

from marshmallow import fields, pre_load, post_dump, Schema, EXCLUDE
from marshmallow.validate import Range

from platypush.schemas import DateTime, EnumField

from ._model import (
    LinodeInstanceBackupScheduleDay,
    LinodeInstanceBackupScheduleWindow,
    LinodeInstanceStatus,
)


class FieldWithId(fields.Function):
    """
    Field that handles values that are objects with an ``id`` attribute.
    """

    def _deserialize(self, value: Any, *_, **__) -> Optional[Any]:
        return value.id if value is not None else None

    def _serialize(self, value: Any, *_, **__) -> Optional[Any]:
        return value


class LinodeBaseSchema(Schema):
    """
    Base schema for Linode objects.
    """

    class Meta:  # type: ignore
        """
        Meta class for the schema.
        """

        unknown = EXCLUDE


class LinodeInstanceSpecsSchema(LinodeBaseSchema):
    """
    Linode instance specifications schema.
    """

    disk = fields.Int(
        metadata={
            'description': 'Allocated disk size, in MB',
            'example': 100000,
        }
    )

    memory = fields.Int(
        metadata={
            'description': 'Allocated RAM size, in MB',
            'example': 8192,
        }
    )

    cpus = fields.Int(
        data_key='vcpus',
        metadata={
            'description': 'Number of virtual CPUs allocated to the instance',
            'example': 4,
        },
    )

    gpus = fields.Int(
        metadata={
            'metadata': {
                'description': 'Number of GPUs allocated to the instance',
                'example': 1,
            }
        }
    )

    transfer = fields.Int(
        metadata={
            'description': (
                'Number of network transfers this instance is allotted each month',
            ),
            'example': 5000,
        }
    )

    @post_dump
    def post_dump(self, data: dict, **_) -> dict:
        if 'vcpus' in data:
            data['cpus'] = data.pop('vcpus')
        return data


class LinodeInstanceAlertsSchema(LinodeBaseSchema):
    """
    Schema that models the alerts configuration of a Linode instance.
    """

    cpu = fields.Int(
        allow_none=True,
        metadata={
            'description': (
                'The percentage of CPU average usage over the past two hours '
                'required to trigger an alert'
            ),
            'example': 90,
        },
    )

    io = fields.Int(
        allow_none=True,
        metadata={
            'description': (
                'The amount of disk I/O operations per second required to '
                'trigger an alert'
            ),
            'example': 5000,
        },
    )

    network_in = fields.Float(
        allow_none=True,
        metadata={
            'description': (
                'The amount of incoming network traffic, in Mbit/s, '
                'required to trigger an alert'
            ),
            'example': 10,
        },
    )

    network_out = fields.Float(
        allow_none=True,
        metadata={
            'description': (
                'The amount of outgoing network traffic, in Mbit/s, '
                'required to trigger an alert'
            ),
            'example': 10,
        },
    )

    transfer_quota = fields.Float(
        allow_none=True,
        metadata={
            'validate': Range(min=0, max=100),
            'description': (
                'The percentage of network transfer that may be used before '
                'an alert is triggered, between 0 and 100'
            ),
            'example': 80,
        },
    )


class LinodeInstanceBackupScheduleSchema(LinodeBaseSchema):
    """
    Schema that models the backup schedule of a Linode instance.
    """

    day = EnumField(
        type=LinodeInstanceBackupScheduleDay,
        allow_none=True,
        metadata={
            'description': 'Day of the week when the backups are scheduled',
            'example': 'Sunday',
        },
    )

    window = EnumField(
        type=LinodeInstanceBackupScheduleWindow,
        allow_none=True,
        metadata={
            'description': 'Time window when the backups are scheduled',
            'example': 'W10',
        },
    )


class LinodeInstanceBackupsSchema(LinodeBaseSchema):
    """
    Schema that models the backup status of a Linode instance.
    """

    available = fields.Bool(
        metadata={
            'description': 'Whether the backups are available for this instance',
            'example': True,
        }
    )

    enabled = fields.Bool(
        metadata={
            'description': 'Whether the backups are enabled on this instance',
            'example': True,
        }
    )

    schedule = fields.Nested(
        LinodeInstanceBackupScheduleSchema,
        metadata={
            'description': 'Backup schedule configuration',
        },
    )

    last_successful = DateTime(
        allow_none=True,
        metadata={
            'description': 'When the last backup was successful',
            'example': '2020-01-01T00:00:00Z',
        },
    )


class LinodeInstanceSchema(LinodeBaseSchema):
    """
    Class that models a Linode instance.
    """

    id = fields.Int(
        required=True,
        metadata={
            'description': 'Instance ID',
            'example': 12345,
        },
    )

    name = fields.String(
        required=True,
        data_key='label',
        metadata={
            'description': 'Instance name',
            'example': 'my-instance',
        },
    )

    instance_type = FieldWithId(
        metadata={
            'description': 'Instance type',
            'example': 'g6-standard-4',
        }
    )

    ipv4_addresses = fields.List(
        fields.String(),
        data_key='ipv4',
        metadata={
            'description': 'List of IPv4 addresses associated with this instance',
            'example': '["1.2.3.4"]',
        },
    )

    ipv6_address = fields.String(
        data_key='ipv6',
        metadata={
            'description': 'IPv6 address associated with this instance',
            'example': '1234:5678::9abc:def0:1234:5678/128',
        },
    )

    group = fields.String(
        metadata={
            'description': 'Group the instance belongs to',
            'example': 'my-group',
        }
    )

    status = EnumField(
        type=LinodeInstanceStatus,
        metadata={
            'description': 'Instance status',
            'example': 'running',
        },
    )

    tags = fields.List(
        fields.String(),
        metadata={
            'description': 'List of tags associated with this instance',
            'example': '["tag1", "tag2"]',
        },
    )

    image = FieldWithId(
        metadata={
            'description': 'Image used to ',
            'example': 'linode/archlinux2014.04',
        }
    )

    region = FieldWithId(
        metadata={
            'description': 'Region where the instance is located',
            'example': 'eu-west',
        }
    )

    hypervisor = fields.String(
        metadata={
            'description': 'The virtualization engine powering this instance',
            'example': 'kvm',
        }
    )

    specs = fields.Nested(LinodeInstanceSpecsSchema)
    alerts = fields.Nested(LinodeInstanceAlertsSchema)
    backups = fields.Nested(LinodeInstanceBackupsSchema)
    created_at = DateTime(
        data_key='created',
        metadata={
            'description': 'Instance creation date',
            'example': '2020-01-01T00:00:00Z',
        },
    )

    updated_at = DateTime(
        data_key='updated',
        metadata={
            'description': 'When the instance was last polled/updated',
            'example': '2020-01-01T01:00:00Z',
        },
    )

    @pre_load
    def pre_load(self, data: dict, **_) -> dict:
        from linode_api4.objects.base import MappedObject

        # Expand MappedObjects to dictionaries
        for key, value in data.items():
            if isinstance(value, MappedObject):
                data[key] = value.dict

        # NOTE Workaround for type -> instance_type not being correctly mapped
        if 'type' in data:
            data['instance_type'] = data.pop('type')

        return data

    @post_dump
    def post_dump(self, data: dict, **_) -> dict:
        for data_key, dump_key in [
            ('label', 'name'),
            ('ipv4', 'ipv4_addresses'),
            ('ipv6', 'ipv6_address'),
            ('created', 'created_at'),
            ('updated', 'updated_at'),
        ]:
            if data_key in data:
                data[dump_key] = data.pop(data_key)

        return data
