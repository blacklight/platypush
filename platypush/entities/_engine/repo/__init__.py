import logging
from typing import Dict, Iterable, Optional, Tuple

from sqlalchemy.orm import Session

from platypush.entities._base import Entity, EntityMapping
from platypush.entities._engine.repo.db import EntitiesDb
from platypush.entities._engine.repo.helpers import get_parent
from platypush.entities._engine.repo.merger import EntitiesMerger

logger = logging.getLogger('entities')


class EntitiesRepository:
    """
    This object is used to get and save entities. It wraps the database
    connection.
    """

    def __init__(self):
        self._db = EntitiesDb()
        self._merge = EntitiesMerger()

    def get(
        self, session: Session, entities: Iterable[Entity]
    ) -> Dict[Tuple[str, str], Entity]:
        """
        Given a set of entity objects, it returns those that already exist
        (or have the same ``entity_key``).
        """
        return self._db.fetch(session, entities)

    def save(self, *entities: Entity) -> Iterable[Entity]:
        """
        Perform an upsert of entities after merging duplicates and rebuilding
        the taxonomies.
        """

        with self._db.get_session(
            locked=True,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        ) as session:
            merged_entities = self._merge(
                session,
                entities,
                existing_entities=self._fetch_all_and_flatten(session, entities),
            )

            merged_entities = self._db.upsert(session, merged_entities)

        return merged_entities

    def _fetch_all_and_flatten(
        self,
        session: Session,
        entities: Iterable[Entity],
    ) -> EntityMapping:
        """
        Given a collection of entities, retrieves their persisted instances
        (lookup is performed by ``entity_key``), and it also recursively
        expands their relationships, so the session is updated with the latest
        persisted versions of all the objects in the hierarchy.

        :return: An ``entity_key -> entity`` mapping.
        """
        expanded_entities = {}
        for entity in entities:
            root_entity = self._get_root_entity(session, entity)
            expanded_entities.update(self._expand_children([root_entity]))
            expanded_entities.update(self._expand_children([entity]))

        return self.get(session, expanded_entities.values())

    @classmethod
    def _expand_children(
        cls,
        entities: Iterable[Entity],
        all_entities: Optional[EntityMapping] = None,
    ) -> EntityMapping:
        """
        Recursively expands and flattens all the children of a set of entities
        into an ``entity_key -> entity`` mapping.
        """
        all_entities = all_entities or {}
        for entity in entities:
            all_entities[entity.entity_key] = entity
            cls._expand_children(entity.children, all_entities)

        return all_entities

    def _get_root_entity(self, session: Session, entity: Entity) -> Entity:
        """
        Retrieve the root entity (i.e. the one with a null parent) of an
        entity.
        """
        parent = entity
        while parent:
            parent = get_parent(session, entity)
            if parent:
                entity = parent

        return entity
