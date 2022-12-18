import logging
from typing import Dict, Iterable, Tuple

from sqlalchemy.orm import Session, make_transient

from platypush.entities import Entity
from platypush.entities._engine.repo.cache import EntitiesCache
from platypush.entities._engine.repo.db import EntitiesDb
from platypush.entities._engine.repo.merger import EntitiesMerger

logger = logging.getLogger('entities')


class EntitiesRepository:
    """
    This object is used to get and save entities, and it wraps database and
    cache objects.
    """

    def __init__(self):
        self._cache = EntitiesCache()
        self._db = EntitiesDb()
        self._merger = EntitiesMerger(self)
        self._init_entities_cache()

    def _init_entities_cache(self):
        """
        Initializes the repository with the existing entities.
        """
        logger.info('Initializing entities cache')
        with self._db.get_session() as session:
            entities = session.query(Entity).all()
            for entity in entities:
                make_transient(entity)

        self._cache.update(*entities, overwrite=True)
        logger.info('Entities cache initialized')

    def get(
        self, session: Session, entities: Iterable[Entity], use_cache=True
    ) -> Dict[Tuple[str, str], Entity]:
        """
        Given a set of entity objects, it returns those that already exist
        (or have the same ``entity_key``). It looks up both the cache and the
        database.
        """
        existing_entities = {}
        if not use_cache:
            existing_entities = self._db.fetch(session, entities)
            self._cache.update(*existing_entities.values())
        else:
            # Fetch the entities that exist in the cache
            existing_entities = {
                e.entity_key: self._cache.get(e) for e in entities if self._cache.get(e)
            }

            # Retrieve from the database the entities that miss from the cache
            cache_miss_entities = {
                e.entity_key: e
                for e in entities
                if e.entity_key not in existing_entities
            }

            cache_miss_existing_entities = self._db.fetch(
                session, cache_miss_entities.values()
            )

            # Update the cache
            self._cache.update(*cache_miss_existing_entities.values())

            # Return the union of the cached + retrieved entities
            existing_entities.update(cache_miss_existing_entities)

        return existing_entities

    def save(self, *entities: Entity) -> Iterable[Entity]:
        """
        Perform an upsert of entities after merging duplicates and rebuilding
        the taxonomies. It updates both the database and the cache.
        """
        with self._db.get_session(locked=True, autoflush=False) as session:
            merged_entities = self._merger.merge(session, entities)
            merged_entities = self._db.upsert(session, merged_entities)
            self._cache.update(*merged_entities, overwrite=True)

        return merged_entities
