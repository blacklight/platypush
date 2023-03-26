from datetime import datetime, timedelta
import logging
from threading import Event
from typing import Collection, Optional

from ._base import (
    Entity,
    EntityKey,
    EntitySavedCallback,
    get_entities_registry,
    init_entities_db,
)
from ._engine import EntitiesEngine
from .managers import (
    EntityManager,
    get_plugin_entity_registry,
    register_entity_manager,
)
from .managers.lights import LightEntityManager
from .managers.sensors import SensorEntityManager
from .managers.switches import (
    DimmerEntityManager,
    EnumSwitchEntityManager,
    SwitchEntityManager,
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


def get_entities_engine(timeout: Optional[float] = None) -> EntitiesEngine:
    """
    Return the running entities engine.

    :param timeout: Timeout in seconds (default: None).
    """
    time_start = datetime.utcnow()
    while not timeout or (datetime.utcnow() - time_start < timedelta(seconds=timeout)):
        if _engine:
            break

        Event().wait(1)

    assert _engine, 'The entities engine has not been initialized'
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
    'EntityKey',
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
