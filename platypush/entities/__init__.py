import logging
from typing import Collection, Optional

from ._base import (
    Entity,
    EntitySavedCallback,
    get_entities_registry,
    init_entities_db,
)
from ._engine import EntitiesEngine
from ._managers import (
    EntityManager,
    get_plugin_entity_registry,
    register_entity_manager,
)
from ._managers.lights import LightEntityManager
from ._managers.sensors import SensorEntityManager
from ._managers.switches import (
    SwitchEntityManager,
    DimmerEntityManager,
    EnumSwitchEntityManager,
)

_engine: Optional[EntitiesEngine] = None
logger = logging.getLogger(__name__)


def init_entities_engine() -> EntitiesEngine:
    """
    Initialize and start the entities engine.
    """
    global _engine  # pylint: disable=global-statement
    init_entities_db()
    _engine = EntitiesEngine()
    _engine.start()
    return _engine


def publish_entities(
    entities: Collection[Entity], callback: Optional[EntitySavedCallback] = None
) -> None:
    """
    Publish a collection of entities to be processed by the engine.

    The engine will:

        - Normalize and merge the provided entities.
        - Trigger ``EntityUpdateEvent`` events.
        - Persist the new state to the local database.

    :param entities: Entities to be published.
    """
    if not _engine:
        logger.debug('No entities engine registered')
        return

    _engine.post(*entities, callback=callback)


__all__ = (
    'DimmerEntityManager',
    'EntitiesEngine',
    'Entity',
    'EntityManager',
    'EntitySavedCallback',
    'EnumSwitchEntityManager',
    'LightEntityManager',
    'SensorEntityManager',
    'SwitchEntityManager',
    'get_entities_registry',
    'get_plugin_entity_registry',
    'init_entities_engine',
    'publish_entities',
    'register_entity_manager',
)
