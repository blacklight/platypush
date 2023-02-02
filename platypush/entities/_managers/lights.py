from abc import ABC, abstractmethod

from .switches import SwitchEntityManager


class LightEntityManager(SwitchEntityManager, ABC):
    """
    Base class for integrations that support light/bulbs entities.
    """

    @abstractmethod
    def set_lights(self, *args, lights=None, **kwargs):
        """
        Set a set of properties on a set of lights.

        :param light: List of lights to set. Each item can represent a light
            name or ID.
        :param kwargs: key-value list of the parameters to set.
        """
        raise NotImplementedError()
