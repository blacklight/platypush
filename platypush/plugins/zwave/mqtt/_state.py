from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple, Union
from threading import RLock

IdType = Union[str, int]
_CacheMap = Dict[IdType, dict]


@dataclass
class Cache:
    """
    Cache class for Z-Wave entities.
    """

    by_id: _CacheMap = field(default_factory=dict)
    by_name: _CacheMap = field(default_factory=dict)
    _lock: RLock = field(default_factory=RLock)

    def add(self, *objs: dict, overwrite: bool = False) -> None:
        """
        Add objects to the cache.
        """
        with self._lock:
            if overwrite:
                self.clear()

            for obj in objs:
                obj_id = obj.get("id")
                if obj_id:
                    self.by_id[obj_id] = obj

                name = self._get_name(obj)
                if name:
                    self.by_name[name] = obj

    def get(
        self,
        obj: Optional[Union[IdType, Tuple[Optional[IdType], Optional[IdType]]]] = None,
        default=None,
    ) -> Optional[dict]:
        """
        Get an object from the cache, by ID or name/label.
        """
        if obj is None:
            return None

        if isinstance(obj, tuple):
            return self.get(obj[0], self.get(obj[1], default))

        return self.by_id.get(obj, self.by_name.get(obj, default))

    def __contains__(self, obj: Optional[IdType]) -> bool:
        """
        Check if an object with the given ID/name is in the cache.
        """
        return obj in self.by_id or obj in self.by_name

    def clear(self) -> None:
        """
        Clear the cache.
        """
        with self._lock:
            self.by_id.clear()
            self.by_name.clear()

    def pop(self, obj_id: IdType, default=None) -> Optional[dict]:
        """
        Remove and return an object from the cache.
        """
        with self._lock:
            obj = self.by_id.pop(obj_id, default)
            if not obj:
                return obj

            name = self._get_name(obj)
            if name:
                self.by_name.pop(name, None)
            return obj

    @staticmethod
    def _get_name(obj: dict) -> Optional[str]:
        """
        @return The name/label of an object.
        """
        return obj.get("name", obj.get("label"))


@dataclass
class State:
    """
    State of the Z-Wave network.
    """

    nodes: Cache = field(default_factory=Cache)
    values: Cache = field(default_factory=Cache)
    scenes: Cache = field(default_factory=Cache)
    groups: Cache = field(default_factory=Cache)
