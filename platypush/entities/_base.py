import inspect
import json
import pathlib
import types
from datetime import datetime
from dateutil.tz import tzutc
from typing import Mapping, Type, Tuple, Any

import pkgutil
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    UniqueConstraint,
    inspect as schema_inspect,
)
from sqlalchemy.orm import ColumnProperty, Mapped, backref, relationship

from platypush.common.db import Base
from platypush.message import JSONAble

entities_registry: Mapping[Type['Entity'], Mapping] = {}


if 'entity' not in Base.metadata:

    class Entity(Base):
        """
        Model for a general-purpose platform entity.
        """

        __tablename__ = 'entity'

        id = Column(Integer, autoincrement=True, primary_key=True)
        external_id = Column(String, nullable=False)
        name = Column(String, nullable=False, index=True)
        description = Column(String)
        type = Column(String, nullable=False, index=True)
        plugin = Column(String, nullable=False)
        parent_id = Column(
            Integer,
            ForeignKey(f'{__tablename__}.id', ondelete='CASCADE'),
            nullable=True,
        )

        data = Column(JSON, default=dict)
        meta = Column(JSON, default=dict)
        is_read_only = Column(Boolean, default=False)
        is_write_only = Column(Boolean, default=False)
        is_query_disabled = Column(Boolean, default=False)
        created_at = Column(
            DateTime(timezone=False), default=datetime.utcnow(), nullable=False
        )
        updated_at = Column(
            DateTime(timezone=False),
            default=datetime.utcnow(),
            onupdate=datetime.utcnow(),
        )

        parent: Mapped['Entity'] = relationship(
            'Entity',
            remote_side=[id],
            uselist=False,
            lazy=True,
            post_update=True,
            backref=backref(
                'children',
                remote_side=[parent_id],
                uselist=True,
                cascade='all, delete-orphan',
                lazy='immediate',
            ),
        )

        UniqueConstraint(external_id, plugin)

        __table_args__ = (
            Index('name_and_plugin_index', name, plugin),
            Index('name_type_and_plugin_index', name, type, plugin),
            {'extend_existing': True},
        )

        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
            'polymorphic_on': type,
        }

        @classmethod
        @property
        def columns(cls) -> Tuple[ColumnProperty]:
            inspector = schema_inspect(cls)
            return tuple(inspector.mapper.column_attrs)

        @property
        def entity_key(self) -> Tuple[str, str]:
            """
            This method returns the "external" key of an entity.
            """
            return (str(self.external_id), str(self.plugin))

        def _serialize_value(self, col: ColumnProperty) -> Any:
            val = getattr(self, col.key)
            if isinstance(val, datetime):
                # All entity timestamps are in UTC
                val = val.replace(tzinfo=tzutc()).isoformat()

            return val

        def to_json(self) -> dict:
            return {col.key: self._serialize_value(col) for col in self.columns}

        def __repr__(self):
            return str(self)

        def __str__(self):
            return json.dumps(self.to_json())

        def __setattr__(self, key, value):
            matching_columns = [c for c in self.columns if c.expression.name == key]

            if (
                matching_columns
                and issubclass(type(matching_columns[0].columns[0].type), DateTime)
                and isinstance(value, str)
            ):
                value = datetime.fromisoformat(value)

            return super().__setattr__(key, value)

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
            mod_loader = loader.find_spec(modname, None)
            assert mod_loader and mod_loader.loader
            module = types.ModuleType(mod_loader.name)
            mod_loader.loader.exec_module(module)
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
    db.create_all(db.get_engine(), Base)
