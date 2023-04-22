import logging
from typing import Iterable, List, Optional

from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import ObjectDeletedError

from platypush.entities._base import Entity, EntityMapping

from .helpers import get_parent

logger = logging.getLogger(__name__)


# pylint: disable=too-few-public-methods
class EntitiesMerger:
    """
    A stateless functor in charge of detecting and merging entities that
    already exist on the database before flushing the session.
    """

    def __call__(
        self,
        session: Session,
        entities: Iterable[Entity],
        existing_entities: Optional[EntityMapping] = None,
    ) -> List[Entity]:
        """
        Merge a set of entities with their existing representations and update
        the parent/child relationships and return a list containing
        ``[*updated_entities, *new_entities]``.
        """
        existing_entities = existing_entities or {}
        new_entities: EntityMapping = {}

        self._merge(
            session,
            entities,
            new_entities=new_entities,
            existing_entities=existing_entities,
        )

        return list({**existing_entities, **new_entities}.values())

    def _merge(
        self,
        session: Session,
        entities: Iterable[Entity],
        new_entities: EntityMapping,
        existing_entities: EntityMapping,
    ) -> List[Entity]:
        """
        (Recursive) inner implementation of the entity merge logic.
        """
        processed_entities = []

        # Retrieve existing records and merge them
        for entity in entities:
            key = entity.entity_key
            existing_entity = existing_entities.get(key, new_entities.get(key))

            # Synchronize the parent(s)
            entity = self._sync_parent(session, entity, new_entities, existing_entities)

            if existing_entity:
                # Merge the columns with those of the existing entity
                existing_entity = self._merge_columns(entity, existing_entity)
                # Merge the children
                self._append_children(
                    existing_entity,
                    *self._merge(
                        session,
                        entity.children,
                        new_entities,
                        existing_entities,
                    )
                )

                # Use the existing entity now that it's been merged
                entity = existing_entity
            else:
                # Add it to the map of new entities if the entity doesn't exist on the db
                new_entities[key] = entity

            processed_entities.append(entity)

        return processed_entities

    @classmethod
    def _sync_parent(
        cls,
        session: Session,
        entity: Entity,
        new_entities: EntityMapping,
        existing_entities: EntityMapping,
    ) -> Entity:
        """
        Recursively refresh the parent of an entity all the way up in the
        hierarchy, to make sure that all the parent/child relations are
        appropriately rewired and that all the relevant objects are added to
        this session.
        """
        parent = get_parent(session, entity)
        if not parent:
            # No parent -> we can terminate the recursive climbing
            return entity

        # Check if an entity with the same key as the reported parent already
        # exists in the cached entities
        existing_parent = existing_entities.get(
            parent.entity_key, new_entities.get(parent.entity_key)
        )

        if not existing_parent:
            # No existing parent -> we need to flush the one reported by this
            # entity
            return entity

        # Check if the existing parent already has a child with the same key as
        # this entity
        existing_entity = next(
            iter(
                child
                for child in existing_parent.children
                if child.entity_key == entity.entity_key
            ),
            None,
        )

        if not existing_entity:
            # If this entity isn't currently a member of the existing parent,
            # temporarily reset the parent of the current entity, so we won't
            # carry stale objects around. We will soon rewire it to the
            # existing parent.
            entity.parent = None
        else:
            # Otherwise, merge the columns of the existing entity with those of
            # the new entity and use the existing entity
            entity = cls._merge_columns(entity, existing_entity, include_children=True)

        # Refresh the existing collection of children with the new/updated
        # entity
        cls._append_children(existing_parent, entity)

        # Recursively call this function to synchronize any parent entities up
        # in the taxonomy
        cls._sync_parent(session, existing_parent, new_entities, existing_entities)
        return entity

    @staticmethod
    def _append_children(entity: Entity, *children: Entity):
        """
        Update the list of children of a given entity with the given list of
        entities.

        Note that, in case of ``entity_key`` conflict (the key of a new entity
        already exists in the entity's children), the most recent version will
        be used, so any column merge logic needs to happen before this method
        is called.
        """
        entity.children = list(
            {
                **{e.entity_key: e for e in entity.children},
                **{e.entity_key: e for e in children},
            }.values()
        )

        for child in children:
            child.parent = entity
            if entity.id:
                child.parent_id = entity.id

    @classmethod
    def _merge_columns(
        cls, entity: Entity, existing_entity: Entity, include_children: bool = False
    ) -> Entity:
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
                try:
                    setattr(existing_entity, col, getattr(entity, col))
                except ObjectDeletedError as e:
                    logger.warning(
                        'Could not set %s on entity <%s>: %s',
                        col, existing_entity.entity_key, e
                    )

        # Recursive call to merge the columns of the children too
        if include_children:
            existing_children = {e.entity_key: e for e in existing_entity.children}
            new_children = {e.entity_key: e for e in entity.children}
            updated_children = {}

            for key, child in new_children.items():
                existing_child = existing_children.get(key)
                updated_children[key] = (
                    cls._merge_columns(child, existing_child, include_children=True)
                    if existing_child
                    else child
                )

            cls._append_children(existing_entity, *updated_children.values())

        return existing_entity
