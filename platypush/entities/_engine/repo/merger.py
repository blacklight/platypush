from typing import Dict, Iterable, List, Optional, Tuple

from sqlalchemy.orm import Session

from platypush.entities import Entity


class EntitiesMerger:
    """
    This object is in charge of detecting and merging entities that already
    exist on the database before flushing the session.
    """

    def __init__(self, repository):
        from . import EntitiesRepository

        self._repo: EntitiesRepository = repository  # type: ignore

    def merge(
        self,
        session: Session,
        entities: Iterable[Entity],
    ) -> List[Entity]:
        """
        Merge a set of entities with their existing representations and update
        the parent/child relationships and return a tuple with
        ``[new_entities, updated_entities]``.
        """
        new_entities: Dict[Tuple[str, str], Entity] = {}
        existing_entities: Dict[Tuple[str, str], Entity] = {}

        self._merge(
            session,
            entities,
            new_entities=new_entities,
            existing_entities=existing_entities,
        )

        return [*existing_entities.values(), *new_entities.values()]

    def _merge(
        self,
        session: Session,
        entities: Iterable[Entity],
        new_entities: Dict[Tuple[str, str], Entity],
        existing_entities: Dict[Tuple[str, str], Entity],
    ) -> List[Entity]:
        """
        (Recursive) inner implementation of the entity merge logic.
        """
        processed_entities = []
        existing_entities.update(self._repo.get(session, entities, use_cache=False))

        # Make sure that we have no duplicate entity keys in the current batch
        entities = list(
            {
                **({e.entity_key: e for e in entities}),
                **(
                    {
                        e.entity_key: e
                        for e in {str(ee.id): ee for ee in entities if ee.id}.values()
                    }
                ),
            }.values()
        )

        # Retrieve existing records and merge them
        for entity in entities:
            key = entity.entity_key
            existing_entity = existing_entities.get(key, new_entities.get(key))
            parent_id, parent = self._update_parent(session, entity, new_entities)

            if existing_entity:
                # Update the parent
                if not parent_id and parent:
                    existing_entity.parent = parent
                else:
                    existing_entity.parent_id = parent_id  # type: ignore

                # Merge the other columns
                self._merge_columns(entity, existing_entity)
                entity = existing_entity
            else:
                # Add it to the map of new entities if the entity doesn't exist
                # on the repo
                new_entities[key] = entity

            processed_entities.append(entity)

        return processed_entities

    def _update_parent(
        self,
        session: Session,
        entity: Entity,
        new_entities: Dict[Tuple[str, str], Entity],
    ) -> Tuple[Optional[int], Optional[Entity]]:
        """
        Recursively update the hierarchy of an entity, moving upwards towards
        the parent.
        """
        parent_id: Optional[int] = entity.parent_id  # type: ignore
        parent: Optional[Entity] = entity.parent

        # If the entity has a parent with an ID, use that
        if parent and parent.id:
            parent_id = parent_id or parent.id

        # If there's no parent_id but there is a parent object, try to fetch
        # its stored version
        if not parent_id and parent:
            batch = list(self._repo.get(session, [parent], use_cache=False).values())

            # If the parent is already stored, use its ID
            if batch:
                parent = batch[0]
                parent_id = parent.id  # type: ignore

            # Otherwise, check if its key is already among those awaiting flush
            # and reuse the same objects (prevents SQLAlchemy from generating
            # duplicate inserts)
            else:
                temp_entity = new_entities.get(parent.entity_key)
                if temp_entity:
                    self._remove_duplicate_children(entity, temp_entity)
                    parent = entity.parent = temp_entity
                else:
                    new_entities[parent.entity_key] = parent

                # Recursively apply any changes up in the hierarchy
                self._update_parent(session, parent, new_entities=new_entities)

        # If we found a parent_id, populate it on the entity (and remove the
        # supporting relationship object so SQLAlchemy doesn't go nuts when
        # flushing)
        if parent_id:
            entity.parent = None
            entity.parent_id = parent_id  # type: ignore

        return parent_id, parent

    @staticmethod
    def _remove_duplicate_children(entity: Entity, parent: Optional[Entity] = None):
        if not parent:
            return

        # Make sure that an entity has no duplicate entity IDs among its
        # children
        existing_child_index_by_id = None
        if entity.id:
            try:
                existing_child_index_by_id = [e.id for e in parent.children].index(
                    entity.id
                )
                parent.children.pop(existing_child_index_by_id)
            except ValueError:
                pass

        # Make sure that an entity has no duplicate entity keys among its
        # children
        existing_child_index_by_key = None
        try:
            existing_child_index_by_key = [e.entity_key for e in parent.children].index(
                entity.entity_key
            )
            parent.children.pop(existing_child_index_by_key)
        except ValueError:
            pass

    @classmethod
    def _merge_columns(cls, entity: Entity, existing_entity: Entity) -> Entity:
        """
        Merge two versions of an entity column by column.
        """
        columns = [col.key for col in entity.columns]
        for col in columns:
            if col == 'meta':
                existing_entity.meta = {  # type: ignore
                    **(existing_entity.meta or {}),  # type: ignore
                    **(entity.meta or {}),  # type: ignore
                }
            elif col not in ('id', 'created_at'):
                setattr(existing_entity, col, getattr(entity, col))

        return existing_entity
