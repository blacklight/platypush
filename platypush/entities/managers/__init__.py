import inspect
import json
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Optional, Dict, Collection, Type

from platypush.config import Config
from platypush.entities._base import Entity, EntitySavedCallback
from platypush.utils import get_plugin_name_by_class, get_redis

_entity_registry_varname = '_platypush/plugin_entity_registry'


class EntityManager(ABC):
    """
    Base mixin for all the integrations that support entities mapping.

    The classes that implement the entity manager need to implement the
    :meth:`.transform_entities` method, which will convert the supported
    entities from whichever format the integration supports to a collection of
    :class:`platypush.entities.Entity` objects.

    The converted entities will then be passed to the
    :class:`platypush.entities.EntitiesEngine` whenever
    :meth:`.publish_entities` is called

    The implemented classes should also implement the :meth:`.status` method.
    This method should retrieve the current state of the entities and call
    :meth:`.publish_entities`.
    """

    def __new__(cls, *_, **__) -> 'EntityManager':
        register_entity_manager(cls)
        return super().__new__(cls)

    @abstractmethod
    def transform_entities(self, entities: Collection[Any]) -> Collection[Entity]:
        """
        This method takes a list of entities in any (plugin-specific)
        format and converts them into a standardized collection of
        `Entity` objects. Since this method is called by
        :meth:`.publish_entities` before entity updates are published,
        you may usually want to extend it to pre-process the entities
        managed by your extension into the standard format before they
        are stored and published to all the consumers.
        """
        assert all(isinstance(e, Entity) for e in entities), (
            'Expected all the instances to be entities, got '
            f'{[e.__class__.__name__ for e in entities]}'
        )
        return entities

    @abstractmethod
    def status(self, *_, **__):
        """
        All derived classes should implement this method.

        At the very least, this method should refresh the current state of the
        integration's entities and call :meth:`.publish_entities`.

        It should also return the current state of the entities as a list of
        serialized entities, if possible.
        """
        raise NotImplementedError(
            'The `status` method has not been implemented in '
            f'{self.__class__.__name__}'
        )

    def _normalize_entities(self, entities: Collection[Entity]) -> Collection[Entity]:
        for entity in entities:
            if not entity:
                continue

            if entity.id and not entity.external_id:
                # Entity IDs can only refer to the internal primary key
                entity.external_id = entity.id
                entity.id = None  # type: ignore

            entity.plugin = get_plugin_name_by_class(self.__class__)  # type: ignore
            entity.updated_at = datetime.utcnow()  # type: ignore
            entity.children = self._normalize_entities(entity.children)

        return entities

    def publish_entities(
        self,
        entities: Optional[Collection[Any]],
        callback: Optional[EntitySavedCallback] = None,
    ) -> Collection[Entity]:
        """
        Publishes a list of entities. The downstream consumers include:

            - The entity persistence manager
            - The web server
            - Any consumer subscribed to
                :class:`platypush.message.event.entities.EntityUpdateEvent`
                events (e.g. web clients)

        It also accepts an optional callback that will be called when each of
        the entities in the set is flushed to the database.

        You usually don't need to override this class (but you may want to
        extend :meth:`.transform_entities` instead if your extension doesn't
        natively handle `Entity` objects).
        """
        from platypush.entities import publish_entities

        transformed_entities = self._normalize_entities(
            self.transform_entities(entities or [])
        )

        publish_entities(transformed_entities, callback=callback)
        return transformed_entities


def register_entity_manager(cls: Type[EntityManager]):
    """
    Associates a plugin as a manager for a certain entity type.
    You usually don't have to call this method directly.
    """
    entity_managers = [c for c in inspect.getmro(cls) if issubclass(c, EntityManager)]

    plugin_name = get_plugin_name_by_class(cls) or ''
    redis = get_redis()
    registry = get_plugin_entity_registry()
    registry_by_plugin = set(registry['by_plugin'].get(plugin_name, []))

    for manager in entity_managers:
        entity_type_name = manager.__name__
        registry_by_type = set(registry['by_type'].get(entity_type_name, []))
        registry_by_plugin.add(entity_type_name)
        registry_by_type.add(plugin_name)
        registry['by_plugin'][plugin_name] = list(registry_by_plugin)
        registry['by_type'][entity_type_name] = list(registry_by_type)

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
        return {'by_plugin': {}, 'by_type': {}}

    enabled_plugins = set(Config.get_plugins().keys())

    return {
        'by_plugin': {
            plugin_name: entity_types
            for plugin_name, entity_types in registry.get('by_plugin', {}).items()
            if plugin_name in enabled_plugins
        },
        'by_type': {
            entity_type: [p for p in plugins if p in enabled_plugins]
            for entity_type, plugins in registry.get('by_type', {}).items()
        },
    }
