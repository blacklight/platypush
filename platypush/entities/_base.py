import inspect
import pathlib
from datetime import datetime
from typing import Mapping, Type, Tuple, Any

import pkgutil
from sqlalchemy import (
    Boolean,
    Column,
    Index,
    Integer,
    String,
    DateTime,
    JSON,
    UniqueConstraint,
    inspect as schema_inspect,
)
from sqlalchemy.orm import declarative_base, ColumnProperty

from platypush.message import JSONAble

Base = declarative_base()
entities_registry: Mapping[Type['Entity'], Mapping] = {}


class Entity(Base):
    """
    Model for a general-purpose platform entity.
    """

    __tablename__ = 'entity'

    id = Column(Integer, autoincrement=True, primary_key=True)
    external_id = Column(String, nullable=True)
    name = Column(String, nullable=False, index=True)
    description = Column(String)
    type = Column(String, nullable=False, index=True)
    plugin = Column(String, nullable=False)
    data = Column(JSON, default=dict)
    meta = Column(JSON, default=dict)
    is_read_only = Column(Boolean, default=False)
    is_write_only = Column(Boolean, default=False)
    created_at = Column(
        DateTime(timezone=False), default=datetime.utcnow(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=False), default=datetime.utcnow(), onupdate=datetime.now()
    )

    UniqueConstraint(external_id, plugin)

    __table_args__ = (Index(name, plugin),)

    __mapper_args__ = {
        'polymorphic_identity': __tablename__,
        'polymorphic_on': type,
    }

    @classmethod
    @property
    def columns(cls) -> Tuple[ColumnProperty]:
        inspector = schema_inspect(cls)
        return tuple(inspector.mapper.column_attrs)

    def _serialize_value(self, col: ColumnProperty) -> Any:
        val = getattr(self, col.key)
        if isinstance(val, datetime):
            # All entity timestamps are in UTC
            val = val.isoformat() + '+00:00'

        return val

    def to_json(self) -> dict:
        return {col.key: self._serialize_value(col) for col in self.columns}

    def get_plugin(self):
        from platypush.context import get_plugin

        plugin = get_plugin(self.plugin)
        assert plugin, f'No such plugin: {plugin}'
        return plugin

    def run(self, action: str, *args, **kwargs):
        plugin = self.get_plugin()
        method = getattr(plugin, action, None)
        assert method, f'No such action: {self.plugin}.{action}'
        return method(self.external_id or self.name, *args, **kwargs)


# Inject the JSONAble mixin (Python goes nuts if done through
# standard multiple inheritance with an SQLAlchemy ORM class)
Entity.__bases__ = Entity.__bases__ + (JSONAble,)


def _discover_entity_types():
    from platypush.context import get_plugin

    logger = get_plugin('logger')
    assert logger

    for loader, modname, _ in pkgutil.walk_packages(
        path=[str(pathlib.Path(__file__).parent.absolute())],
        prefix=__package__ + '.',
        onerror=lambda _: None,
    ):
        try:
            mod_loader = loader.find_module(modname)  # type: ignore
            assert mod_loader
            module = mod_loader.load_module()  # type: ignore
        except Exception as e:
            logger.warning(f'Could not import module {modname}')
            logger.exception(e)
            continue

        for _, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and issubclass(obj, Entity):
                entities_registry[obj] = {}


def get_entities_registry():
    return entities_registry.copy()


def init_entities_db():
    from platypush.context import get_plugin

    _discover_entity_types()
    db = get_plugin('db')
    assert db
    engine = db.get_engine()
    db.create_all(engine, Base)
