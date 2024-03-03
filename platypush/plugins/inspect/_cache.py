from contextlib import contextmanager
import gzip
import json
import logging
from collections import defaultdict
from time import time
from threading import RLock
from typing import Dict, Optional

from platypush.backend import Backend
from platypush.message.event import Event
from platypush.message.response import Response
from platypush.plugins import Plugin
from platypush.utils import (
    get_backend_class_by_name,
    get_backend_name_by_class,
    get_plugin_class_by_name,
    get_plugin_name_by_class,
)

logger = logging.getLogger(__name__)


class Cache:
    """
    A cache for the parsed integration metadata.

    Cache structure:

      .. code-block:: python

        {
            <integration_category>: {
                <integration_type>: {
                    'doc': <integration_docstring>,
                    'args': {
                        <arg_name>: {
                            'name': <arg_name>,
                            'type': <arg_type>,
                            'doc': <arg_docstring>,
                            'default': <arg_default_value>,
                            'required': <arg_required>,
                        },
                        ...
                    },
                    'actions': {
                        <action_name>: {
                            'name': <action_name>,
                            'doc': <action_docstring>,
                            'args': {
                                ...
                            },
                            'returns': {
                                'type': <return_type>,
                                'doc': <return_docstring>,
                            },
                        },
                        ...
                    },
                    'events': [
                        <event_type1>,
                        <event_type2>,
                        ...
                    ],
                },
                ...
            },
            ...
        }

    """

    cur_version = 1.1
    """
    Cache version, used to detect breaking changes in the cache logic that require a cache refresh.
    """

    def __init__(
        self,
        items: Optional[Dict[type, Dict[type, dict]]] = None,
        saved_at: Optional[float] = None,
        loaded_at: Optional[float] = None,
        version: float = cur_version,
    ):
        self.saved_at = saved_at
        self.loaded_at = loaded_at
        self._cache: Dict[type, Dict[type, dict]] = defaultdict(dict)
        self._lock = RLock()
        self.version = version
        self.has_changes = False

        if items:
            self._cache.update(items)
            self.loaded_at = time()

    @classmethod
    def load(cls, cache_file: str) -> 'Cache':
        """
        Loads the components cache from disk.

        :param cache_file: Cache file path.
        """
        with gzip.open(cache_file, 'rb') as f:
            data = f.read()

        return cls.from_dict(json.loads(data.decode()))

    def dump(self, cache_file: str):
        """
        Dumps the components cache to disk.

        :param cache_file: Cache file path.
        """
        from platypush.message import Message

        self.version = self.cur_version
        self.saved_at = time()
        compressed_cache = gzip.compress(
            json.dumps(
                {
                    'saved_at': self.saved_at,
                    'version': self.version,
                    'items': self.to_dict(),
                },
                cls=Message.Encoder,
                sort_keys=True,
            ).encode()
        )

        with open(cache_file, 'wb') as f:
            f.write(compressed_cache)

        self.has_changes = False

    @classmethod
    def from_dict(cls, data: dict) -> 'Cache':
        """
        Creates a cache from a JSON-serializable dictionary.
        """
        return cls(
            items={
                Backend: {
                    k: v
                    for k, v in {
                        get_backend_class_by_name(backend_type): backend_meta
                        for backend_type, backend_meta in data.get('items', {})
                        .get('backends', {})
                        .items()
                    }.items()
                    if k
                },
                Plugin: {
                    k: v
                    for k, v in {
                        get_plugin_class_by_name(plugin_type): plugin_meta
                        for plugin_type, plugin_meta in data.get('items', {})
                        .get('plugins', {})
                        .items()
                    }.items()
                    if k
                },
                Event: data.get('items', {}).get('events', {}),
                Response: data.get('items', {}).get('responses', {}),
            },
            loaded_at=time(),
            saved_at=data.get('saved_at'),
            version=data.get('version', cls.cur_version),
        )

    def to_dict(self) -> Dict[str, Dict[str, dict]]:
        """
        Converts the cache items to a JSON-serializable dictionary.
        """
        return {
            'backends': {
                k: v
                for k, v in {
                    get_backend_name_by_class(backend_type): backend_meta
                    for backend_type, backend_meta in self.backends.items()
                }.items()
                if k
            },
            'plugins': {
                k: v
                for k, v in {
                    get_plugin_name_by_class(plugin_type): plugin_meta
                    for plugin_type, plugin_meta in self.plugins.items()
                }.items()
                if k
            },
            'events': {
                (k if isinstance(k, str) else f'{k.__module__}.{k.__qualname__}'): v
                for k, v in self.events.items()
                if k
            },
            'responses': {
                (k if isinstance(k, str) else f'{k.__module__}.{k.__qualname__}'): v
                for k, v in self.responses.items()
                if k
            },
        }

    def get(self, category: type, obj_type: Optional[type] = None) -> Optional[dict]:
        """
        Retrieves an object from the cache.

        :param category: Category type.
        :param obj_type: Object type.
        :return: Object metadata.
        """
        collection = self._cache[category]
        if not obj_type:
            return collection
        return collection.get(obj_type)

    def set(self, category: type, obj_type: type, value: dict):
        """
        Set an object on the cache.

        :param category: Category type.
        :param obj_type: Object type.
        :param value: Value to set.
        """
        self._cache[category][obj_type] = value
        self.has_changes = True

    @property
    def plugins(self) -> Dict[type, dict]:
        """Plugins metadata."""
        return self._cache[Plugin]

    @property
    def backends(self) -> Dict[type, dict]:
        """Backends metadata."""
        return self._cache[Backend]

    @property
    def events(self) -> Dict[type, dict]:
        """Events metadata."""
        return self._cache[Event]

    @property
    def responses(self) -> Dict[type, dict]:
        """Responses metadata."""
        return self._cache[Response]

    @contextmanager
    def lock(self):
        """
        Context manager that acquires a lock on the cache.
        """
        with self._lock:
            yield
