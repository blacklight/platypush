from threading import RLock
from typing import Dict, Optional, Tuple

from platypush.entities import Entity


class EntitiesCache:
    """
    An auxiliary class to model an entities lookup cache with multiple keys.
    """

    def __init__(self):
        self.by_id: Dict[str, Entity] = {}
        self.by_external_id_and_plugin: Dict[Tuple[str, str], Entity] = {}
        self._lock = RLock()

    def get(self, entity: Entity) -> Optional[Entity]:
        """
        Retrieve the cached representation of an entity, if it exists.
        """
        if entity.id:
            e = self.by_id.get(str(entity.id))
            if e:
                return e

        if entity.external_id and entity.plugin:
            e = self.by_external_id_and_plugin.get(
                (str(entity.external_id), str(entity.plugin))
            )
            if e:
                return e

    def update(self, *entities: Entity, overwrite=False):
        """
        Update the cache with a list of new entities.
        """
        with self._lock:
            for entity in entities:
                if not overwrite:
                    existing_entity = self.by_id.get(str(entity.id))
                    if existing_entity:
                        for k, v in existing_entity.to_json().items():
                            if getattr(entity, k, None) is None:
                                setattr(entity, k, v)

                if entity.id:
                    self.by_id[str(entity.id)] = entity
                if entity.external_id and entity.plugin:
                    self.by_external_id_and_plugin[
                        (str(entity.external_id), str(entity.plugin))
                    ] = entity
