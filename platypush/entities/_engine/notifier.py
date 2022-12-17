from platypush.context import get_bus
from platypush.entities import Entity
from platypush.message.event.entities import EntityUpdateEvent

from platypush.entities._engine.repo.cache import EntitiesCache


class EntityNotifier:
    """
    This object is in charge of forwarding EntityUpdateEvent instances on the
    application bus when some entities are changed.
    """

    def __init__(self, cache: EntitiesCache):
        self._cache = cache
        self._entities_awaiting_flush = set()

    def _populate_entity_id_from_cache(self, new_entity: Entity):
        cached_entity = self._cache.get(new_entity)
        if cached_entity and cached_entity.id:
            new_entity.id = cached_entity.id
        if new_entity.id:
            self._cache.update(new_entity)

    def notify(self, entity: Entity):
        """
        Trigger an EntityUpdateEvent if the entity has been persisted, or queue
        it to the list of entities whose notifications will be flushed when the
        session is committed.
        """
        self._populate_entity_id_from_cache(entity)
        if entity.id:
            get_bus().post(EntityUpdateEvent(entity=entity))
        else:
            self._entities_awaiting_flush.add(entity.entity_key)

    def flush(self, *entities: Entity):
        """
        Flush and process any entities with pending EntityUpdateEvent
        notifications.
        """
        entities_awaiting_flush = {*self._entities_awaiting_flush}
        for entity in entities:
            key = entity.entity_key
            if key in entities_awaiting_flush:
                self.notify(entity)
                self._entities_awaiting_flush.remove(key)
