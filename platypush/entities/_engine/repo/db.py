from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from platypush.context import get_plugin
from platypush.entities._base import Entity
from .helpers import get_parent


@dataclass
class _TaxonomyAwareEntity:
    """
    A support class used to map an entity and its level within a taxonomy to be
    flushed to the database.
    """

    entity: Entity
    level: int


class EntitiesDb:
    """
    This object is a facade around the entities database. It shouldn't be used
    directly. Instead, it is encapsulated by
    :class:`platypush.entities._repo.EntitiesRepository`, which is in charge of
    caching as well.
    """

    def get_session(self, *args, **kwargs) -> Session:
        db = get_plugin('db')
        assert db
        return db.get_session(*args, **kwargs)

    def fetch(
        self, session: Session, entities: Iterable[Entity]
    ) -> Dict[Tuple[str, str], Entity]:
        """
        Given a set of entities, it returns those that already exist on the database.
        """
        if not entities:
            return {}

        entities_filter = or_(
            *[
                and_(
                    Entity.external_id == entity.external_id,
                    Entity.plugin == entity.plugin,
                )
                for entity in entities
            ]
        )

        query = session.query(Entity).filter(entities_filter)
        existing_entities = {entity.entity_key: entity for entity in query.all()}

        return {
            entity.entity_key: existing_entities[entity.entity_key]
            for entity in entities
            if existing_entities.get(entity.entity_key)
        }

    @staticmethod
    def _close_batch(batch: List[_TaxonomyAwareEntity], batches: List[List[Entity]]):
        if batch:
            batches.append([item.entity for item in batch])

            batch.clear()

    def _split_entity_batches_for_flush(
        self, session: Session, entities: Iterable[Entity]
    ) -> List[List[Entity]]:
        """
        This method retrieves the root entities given a list of entities and
        generates batches of "flushable" entities ready for upsert using a BFS
        algorithm.

        This is needed because we want hierarchies of entities to be flushed
        starting from the top layer, once their parents have been appropriately
        rewired. Otherwise, we may end up with conflicts on entities that have
        already been flushed.
        """
        # Index children by parent_id and by parent_key
        children_by_parent_id: Dict[int, Dict[Tuple[str, str], Entity]] = defaultdict(
            lambda: defaultdict(Entity)
        )

        children_by_parent_key: Dict[
            Tuple[str, str], Dict[Tuple[str, str], Entity]
        ] = defaultdict(lambda: defaultdict(Entity))

        for entity in entities:
            parent_key = None
            parent_id = entity.parent_id
            parent = get_parent(session, entity)
            if parent:
                parent_id = parent_id or parent.id
                parent_key = parent.entity_key

            if parent_id:
                children_by_parent_id[parent_id][entity.entity_key] = entity
            if parent_key:
                children_by_parent_key[parent_key][entity.entity_key] = entity

        # Find the root entities in the hierarchy (i.e. those that have a null
        # parent)
        root_entities = list(
            {
                e.entity_key: e
                for e in entities
                if e.parent is None and e.parent_id is None
            }.values()
        )

        # Prepare a list of entities to process through BFS starting with the
        # root nodes (i.e. level=0)
        entities_to_process = [
            _TaxonomyAwareEntity(entity=e, level=0) for e in root_entities
        ]

        batches: List[List[Entity]] = []
        current_batch: List[_TaxonomyAwareEntity] = []

        while entities_to_process:
            # Pop the first element in the list (FIFO implementation)
            item = entities_to_process.pop(0)
            entity = item.entity
            level = item.level

            # If the depth has increased compared to the previous node, flush
            # the current batch and open a new one.
            if current_batch and current_batch[-1].level < level:
                self._close_batch(current_batch, batches)
            current_batch.append(item)

            # Index the children nodes by key
            children_to_process = {
                e.entity_key: e
                for e in children_by_parent_key.get(entity.entity_key, {}).values()
            }

            # If this entity has already been persisted, add back its children
            # that haven't been updated, so we won't lose those connections
            if entity.id:
                children_to_process.update(
                    {
                        e.entity_key: e
                        for e in children_by_parent_id.get(entity.id, {}).values()
                    }
                )

            # Add all the updated+inserted+existing children to the next layer
            # to be expanded
            entities_to_process += [
                _TaxonomyAwareEntity(entity=e, level=level + 1)
                for e in children_to_process.values()
            ]

        # Close any pending batches
        self._close_batch(current_batch, batches)
        return batches

    def upsert(
        self,
        session: Session,
        entities: Iterable[Entity],
    ) -> Iterable[Entity]:
        """
        Persist a set of entities.
        """
        # Get the "unwrapped" batches
        batches = self._split_entity_batches_for_flush(session, entities)

        # Flush each batch as we process it
        for batch in batches:
            session.add_all(batch)
            session.flush()

        session.commit()

        # Make a copy of the entities in the batch, so they can be used outside
        # of this session/thread without the DetachedInstanceError pain
        return list(
            {
                entity.entity_key: entity.copy()
                for batch in batches
                for entity in batch
            }.values()
        )
