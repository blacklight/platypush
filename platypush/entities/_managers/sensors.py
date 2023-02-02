from abc import ABC

from . import EntityManager


class SensorEntityManager(EntityManager, ABC):
    """
    Base class for integrations that support sensor entities.
    """
