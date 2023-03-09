import logging
from typing import Dict, Iterable, Tuple

from sqlalchemy.orm import Session

from platypush.entities import Entity

# pylint: disable=no-name-in-module
from platypush.entities._engine.repo.db import EntitiesDb
from platypush.entities._engine.repo.merger import EntitiesMerger

logger = logging.getLogger('entities')


class EntitiesRepository:
    """
    This object is used to get and save entities. It wraps the database
    connection.
    """

    def __init__(self):
        self._db = EntitiesDb()
        self._merger = EntitiesMerger(self)

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
            merged_entities = self._merger.merge(session, entities)
            merged_entities = self._db.upsert(session, merged_entities)

        return merged_entities
