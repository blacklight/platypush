import logging
from typing import Collection, Optional

from ._base import Entity, get_entities_registry
from ._engine import EntitiesEngine
from ._registry import manages, register_entity_plugin, get_plugin_entity_registry

_engine: Optional[EntitiesEngine] = None
logger = logging.getLogger(__name__)


def init_entities_engine() -> EntitiesEngine:
    from ._base import init_entities_db

    global _engine
    init_entities_db()
    _engine = EntitiesEngine()
    _engine.start()
    return _engine


def publish_entities(entities: Collection[Entity]):
    if not _engine:
        logger.debug('No entities engine registered')
        return

    _engine.post(*entities)


__all__ = (
    'Entity',
    'EntitiesEngine',
    'init_entities_engine',
    'publish_entities',
    'register_entity_plugin',
    'get_plugin_entity_registry',
    'get_entities_registry',
    'manages',
)
