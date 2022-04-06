import json
from datetime import datetime
from typing import Optional, Dict, Collection, Type

from platypush.config import Config
from platypush.plugins import Plugin
from platypush.utils import get_plugin_name_by_class, get_redis

from ._base import Entity

_entity_registry_varname = '_platypush/plugin_entity_registry'


def register_entity_plugin(entity_type: Type[Entity], plugin: Plugin):
    """
    Associates a plugin as a manager for a certain entity type.
    If you use the `@manages` decorator then you usually don't have
    to call this method directly.
    """
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
    """
    Get the `plugin->entity_types` and `entity_type->plugin`
    mappings supported by the current configuration.
    """
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
    """
    This mixin is injected on the fly into any plugin class declared with
    the @manages decorator. The class will therefore implement the
    `publish_entities` and `transform_entities` methods, which can be
    overridden if required.
    """

    def transform_entities(self, entities):
        """
        This method takes a list of entities in any (plugin-specific)
        format and converts them into a standardized collection of
        `Entity` objects. Since this method is called by
        :meth:`.publish_entities` before entity updates are published,
        you may usually want to extend it to pre-process the entities
        managed by your extension into the standard format before they
        are stored and published to all the consumers.
        """
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
        """
        Publishes a list of entities. The downstream consumers include:

            - The entity persistence manager
            - The web server
            - Any consumer subscribed to
                :class:`platypush.message.event.entities.EntityUpdateEvent`
                events (e.g. web clients)

        If your extension class uses the `@manages` decorator then you usually
        don't need to override this class (but you may want to extend
        :meth:`.transform_entities` instead if your extension doesn't natively
        handle `Entity` objects).
        """
        from . import publish_entities

        entities = self.transform_entities(entities)
        publish_entities(entities)


def manages(*entities: Type[Entity]):
    """
    This decorator is used to register a plugin/backend class as a
    manager of one or more types of entities.
    """

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
