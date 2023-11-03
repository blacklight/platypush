from abc import ABC, abstractmethod


class Serializable(ABC):
    """
    Base class for reflection entities that can be serialized to JSON/YAML.
    """

    @abstractmethod
    def to_dict(self) -> dict:
        """
        Serialize the entity to a string.
        """
        raise NotImplementedError()
