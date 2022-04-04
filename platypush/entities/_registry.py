from datetime import datetime
from typing import Optional, Mapping, Dict, Collection, Type

from platypush.plugins import Plugin
from platypush.utils import get_plugin_name_by_class

from ._base import Entity

_entity_plugin_registry: Mapping[Type[Entity], Dict[str, Plugin]] = {}


def register_entity_plugin(entity_type: Type[Entity], plugin: Plugin):
    plugins = _entity_plugin_registry.get(entity_type, {})
    plugin_name = get_plugin_name_by_class(plugin.__class__)
    assert plugin_name
    plugins[plugin_name] = plugin
    _entity_plugin_registry[entity_type] = plugins


def get_plugin_registry():
    return _entity_plugin_registry.copy()


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

