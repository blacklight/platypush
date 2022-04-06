import json
from datetime import datetime
from typing import Optional, Dict, Collection, Type

from platypush.config import Config
from platypush.plugins import Plugin
from platypush.utils import get_plugin_name_by_class, get_redis

from ._base import Entity

_entity_registry_varname = '_platypush/plugin_entity_registry'


def register_entity_plugin(entity_type: Type[Entity], plugin: Plugin):
    plugin_name = get_plugin_name_by_class(plugin.__class__) or ''
    entity_type_name = entity_type.__name__.lower()
    redis = get_redis()
    registry = get_plugin_entity_registry()
    registry_by_plugin = set(registry['by_plugin'].get(plugin_name, []))

    registry_by_entity_type = set(registry['by_entity_type'].get(entity_type_name, []))

    registry_by_plugin.add(entity_type_name)
    registry_by_entity_type.add(plugin_name)
    registry['by_plugin'][plugin_name] = list(registry_by_plugin)
    registry['by_entity_type'][entity_type_name] = list(registry_by_entity_type)
    redis.mset({_entity_registry_varname: json.dumps(registry)})


def get_plugin_entity_registry() -> Dict[str, Dict[str, Collection[str]]]:
    redis = get_redis()
    registry = redis.mget([_entity_registry_varname])[0]
    try:
        registry = json.loads((registry or b'').decode())
    except (TypeError, ValueError):
        return {'by_plugin': {}, 'by_entity_type': {}}

    enabled_plugins = set(Config.get_plugins().keys())

    return {
        'by_plugin': {
            plugin_name: entity_types
            for plugin_name, entity_types in registry['by_plugin'].items()
            if plugin_name in enabled_plugins
        },
        'by_entity_type': {
            entity_type: [p for p in plugins if p in enabled_plugins]
            for entity_type, plugins in registry['by_entity_type'].items()
        },
    }


class EntityManagerMixin:
    def transform_entities(self, entities):
        entities = entities or []
        for entity in entities:
            if entity.id:
                # Entity IDs can only refer to the internal primary key
                entity.external_id = entity.id
                entity.id = None  # type: ignore

            entity.plugin = get_plugin_name_by_class(self.__class__)  # type: ignore
            entity.updated_at = datetime.utcnow()

        return entities

    def publish_entities(self, entities: Optional[Collection[Entity]]):
        from . import publish_entities

        entities = self.transform_entities(entities)
        publish_entities(entities)


def manages(*entities: Type[Entity]):
    def wrapper(plugin: Type[Plugin]):
        init = plugin.__init__

        def __init__(self, *args, **kwargs):
            for entity_type in entities:
                register_entity_plugin(entity_type, self)

            init(self, *args, **kwargs)

        plugin.__init__ = __init__
        # Inject the EntityManagerMixin
        if EntityManagerMixin not in plugin.__bases__:
            plugin.__bases__ = (EntityManagerMixin,) + plugin.__bases__

        return plugin

    return wrapper
