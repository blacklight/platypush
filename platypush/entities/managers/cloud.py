from abc import ABC, abstractmethod
from typing import Union
from uuid import UUID

from . import EntityManager

InstanceId = Union[str, int, UUID]


class CloudInstanceEntityManager(EntityManager, ABC):
    """
    Base class for integrations that support cloud instances (like Linode or
    AWS).
    """

    @abstractmethod
    def reboot(self, instance: InstanceId, **_):
        """
        Reboot an instance.

        :param instance: ID or name of the instance to be rebooted.
        """
        raise NotImplementedError()

    @abstractmethod
    def boot(self, instance: InstanceId, **_):
        """
        Boot an instance.

        :param instance: ID or name of the instance to be rebooted.
        """
        raise NotImplementedError()

    @abstractmethod
    def shutdown(self, instance: InstanceId, **_):
        """
        Shutdown an instance.

        :param instance: ID or name of the instance to be rebooted.
        """
        raise NotImplementedError()
