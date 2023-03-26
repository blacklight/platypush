from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from functools import partial
from typing import Any, List, Optional

from marshmallow import pre_load
from marshmallow.fields import Function
from marshmallow.validate import Range
from marshmallow_dataclass import class_schema

from platypush.schemas import EnumField
from platypush.schemas.dataclasses import DataClassSchema


class LinodeInstanceStatus(Enum):
    """
    Maps the possible states of an instance.
    """

    RUNNING = 'running'
    OFFLINE = 'offline'
    BOOTING = 'booting'
    REBOOTING = 'rebooting'
    SHUTTING_DOWN = 'shutting_down'
    PROVISIONING = 'provisioning'
    DELETING = 'deleting'
    MIGRATING = 'migrating'
    REBUILDING = 'rebuilding'
    CLONING = 'cloning'
    RESTORING = 'restoring'
    STOPPED = 'stopped'


class LinodeInstanceBackupScheduleDay(Enum):
    """
    Allowed values for ``backups.schedule.day``.
    """

    SCHEDULING = 'Scheduling'
    SUNDAY = 'Sunday'
    MONDAY = 'Monday'
    TUESDAY = 'Tuesday'
    WEDNESDAY = 'Wednesday'
    THURSDAY = 'Thursday'
    FRIDAY = 'Friday'
    SATURDAY = 'Saturday'


class LinodeInstanceBackupScheduleWindow(Enum):
    """
    Allowed values for ``backups.schedule.window``.

    The window in which your backups will be taken, in UTC. A backups window is
    a two-hour span of time in which the backup may occur.

    For example, W10 indicates that your backups should be taken between 10:00
    and 12:00.
    """

    SCHEDULING = 'Scheduling'
    W0 = 'W0'
    W2 = 'W2'
    W4 = 'W4'
    W6 = 'W6'
    W8 = 'W8'
    W10 = 'W10'
    W12 = 'W12'
    W14 = 'W14'
    W16 = 'W16'
    W18 = 'W18'
    W20 = 'W20'
    W22 = 'W22'


class FieldWithId(Function):
    """
    Field that handles values that are objects with an ``id`` attribute.
    """

    def _deserialize(self, value: Any, *_, **__) -> Optional[Any]:
        return value.id if value is not None else None

    def _serialize(self, value: Any, *_, **__) -> Optional[Any]:
        return value


class LinodeBaseSchema(DataClassSchema):
    """
    Base schema for all Linode objects.
    """

    TYPE_MAPPING = {
        LinodeInstanceStatus: partial(  # type: ignore
            EnumField, type=LinodeInstanceStatus
        ),
        LinodeInstanceBackupScheduleDay: partial(  # type: ignore
            EnumField, type=LinodeInstanceBackupScheduleDay
        ),
        LinodeInstanceBackupScheduleWindow: partial(  # type: ignore
            EnumField, type=LinodeInstanceBackupScheduleWindow
        ),
        **DataClassSchema.TYPE_MAPPING,
    }

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


@dataclass
class LinodeInstanceSpecs:
    """
    Class that models the specifications of a Linode instance.
    """

    disk: int = field(
        metadata={
            'metadata': {
                'description': 'Allocated disk size, in MB',
                'example': 100000,
            }
        }
    )

    memory: int = field(
        metadata={
            'metadata': {
                'description': 'Allocated RAM size, in MB',
                'example': 8192,
            }
        }
    )

    cpus: int = field(
        metadata={
            'data_key': 'vcpus',
            'metadata': {
                'description': 'Number of virtual CPUs allocated to the instance',
                'example': 4,
            },
        }
    )

    gpus: int = field(
        metadata={
            'metadata': {
                'description': 'Number of GPUs allocated to the instance',
                'example': 1,
            }
        }
    )

    transfer: int = field(
        metadata={
            'metadata': {
                'description': (
                    'Number of network transfers this instance is allotted each month',
                ),
                'example': 5000,
            }
        }
    )


@dataclass
class LinodeInstanceAlerts:
    """
    Class that models the alerts configuration of a Linode instance.
    """

    cpu: int = field(
        metadata={
            'metadata': {
                'validate': Range(min=0, max=100),
                'description': (
                    'The percentage of CPU average usage over the past two hours '
                    'required to trigger an alert',
                ),
                'example': 90,
            }
        }
    )

    io: int = field(
        metadata={
            'metadata': {
                'description': (
                    'The amount of disk I/O operations per second required to '
                    'trigger an alert'
                ),
                'example': 5000,
            }
        }
    )

    network_in: int = field(
        metadata={
            'metadata': {
                'description': (
                    'The amount of incoming network traffic, in Mbit/s, '
                    'required to trigger an alert'
                ),
                'example': 10,
            }
        }
    )

    network_out: int = field(
        metadata={
            'metadata': {
                'description': (
                    'The amount of outgoing network traffic, in Mbit/s, '
                    'required to trigger an alert'
                ),
                'example': 10,
            }
        }
    )

    transfer_quota: int = field(
        metadata={
            'metadata': {
                'validate': Range(min=0, max=100),
                'description': (
                    'The percentage of network transfer that may be used before '
                    'an alert is triggered',
                ),
                'example': 80,
            }
        }
    )


@dataclass
class LinodeInstanceBackupSchedule:
    """
    Class that models the backup schedule of a Linode instance.
    """

    day: Optional[LinodeInstanceBackupScheduleDay]
    window: Optional[LinodeInstanceBackupScheduleWindow]


@dataclass
class LinodeInstanceBackups:
    """
    Class that models the backup status of a Linode instance.
    """

    available: bool
    enabled: bool = field(
        metadata={
            'metadata': {
                'description': 'Whether the backups are enabled on this instance',
                'example': True,
            }
        }
    )

    schedule: LinodeInstanceBackupSchedule
    last_successful: Optional[datetime] = field(
        metadata={
            'metadata': {
                'description': 'When the last backup was successful',
                'example': '2020-01-01T00:00:00Z',
            }
        }
    )


@dataclass
class LinodeInstance:
    """
    Class that models a Linode instance.
    """

    id: int = field(
        metadata={
            'required': True,
            'metadata': {
                'description': 'Instance ID',
                'example': 12345,
            },
        }
    )

    name: str = field(
        metadata={
            'required': True,
            'data_key': 'label',
            'metadata': {
                'description': 'Instance name',
                'example': 'my-instance',
            },
        },
    )

    instance_type: str = field(
        metadata={
            'marshmallow_field': FieldWithId(),
            'metadata': {
                'description': 'Instance type',
                'example': 'g6-standard-4',
            },
        }
    )

    ipv4_addresses: List[str] = field(
        metadata={
            'data_key': 'ipv4',
            'metadata': {
                'description': 'List of IPv4 addresses associated with this instance',
                'example': '["1.2.3.4"]',
            },
        }
    )

    ipv6_address: str = field(
        metadata={
            'data_key': 'ipv6',
            'metadata': {
                'description': 'IPv6 address associated with this instance',
                'example': '1234:5678::9abc:def0:1234:5678/128',
            },
        }
    )

    group: str = field(
        metadata={
            'metadata': {
                'description': 'Group the instance belongs to',
                'example': 'my-group',
            }
        }
    )

    status: LinodeInstanceStatus = field(
        metadata={
            'metadata': {
                'description': 'Instance status',
                'example': 'running',
            }
        }
    )

    tags: List[str] = field(
        metadata={
            'metadata': {
                'description': 'List of tags associated with this instance',
                'example': '["tag1", "tag2"]',
            }
        }
    )

    image: str = field(
        metadata={
            'marshmallow_field': FieldWithId(),
            'metadata': {
                'description': 'Image used to ',
                'example': 'linode/archlinux2014.04',
            },
        }
    )

    region: str = field(
        metadata={
            'marshmallow_field': FieldWithId(),
            'metadata': {
                'description': 'Region where the instance is located',
                'example': 'eu-west',
            },
        }
    )

    hypervisor: str = field(
        metadata={
            'metadata': {
                'description': 'The virtualization engine powering this instance',
                'example': 'kvm',
            }
        }
    )

    specs: LinodeInstanceSpecs
    alerts: LinodeInstanceAlerts
    backups: LinodeInstanceBackups

    created_at: datetime = field(
        metadata={
            'data_key': 'created',
            'metadata': {
                'description': 'Instance creation date',
                'example': '2020-01-01T00:00:00Z',
            },
        }
    )

    updated_at: datetime = field(
        metadata={
            'data_key': 'updated',
            'metadata': {
                'description': 'When the instance was last polled/updated',
                'example': '2020-01-01T01:00:00Z',
            },
        }
    )


LinodeInstanceSchema = class_schema(LinodeInstance, base_schema=LinodeBaseSchema)
