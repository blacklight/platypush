from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional


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


@dataclass
class LinodeInstanceSpecs:
    """
    Class that models the specifications of a Linode instance.
    """

    disk: int
    memory: int
    cpus: int
    gpus: int
    transfer: int


@dataclass
class LinodeInstanceAlerts:
    """
    Class that models the alerts configuration of a Linode instance.
    """

    cpu: int
    io: int
    network_in: int
    network_out: int
    transfer_quota: int


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
    enabled: bool
    schedule: Optional[LinodeInstanceBackupSchedule] = None
    last_successful: Optional[datetime] = None


@dataclass
class LinodeInstance:
    """
    Class that models a Linode instance.
    """

    id: int
    name: str
    instance_type: str
    ipv4_addresses: List[str]
    ipv6_address: str
    group: str
    status: LinodeInstanceStatus
    tags: List[str]
    image: str
    region: str
    hypervisor: str
    specs: LinodeInstanceSpecs
    alerts: LinodeInstanceAlerts
    backups: LinodeInstanceBackups
    created_at: datetime
    updated_at: datetime
