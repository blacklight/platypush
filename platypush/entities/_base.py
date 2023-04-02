import inspect
import json
import pathlib
import types
from datetime import datetime
import pkgutil
from typing import Callable, Dict, Final, Set, Type, Tuple, Any

from dateutil.tz import tzutc
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
from platypush.message import JSONAble, Message

EntityRegistryType = Dict[str, Type['Entity']]
entities_registry: EntityRegistryType = {}

EntityKey = Tuple[str, str]
""" The entity's logical key, as an ``<external_id, plugin>`` tuple. """
EntityMapping = Dict[EntityKey, 'Entity']
""" Internal mapping for entities used for deduplication/merge/upsert. """

_import_error_ignored_modules: Final[Set[str]] = {'bluetooth'}
"""
ImportError exceptions will be ignored for these entity submodules when
imported dynamically. An ImportError for these modules means that some optional
requirements are missing, and if those plugins aren't enabled then we shouldn't
fail.
"""


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
        is_configuration = Column(Boolean, default=False)
        external_url = Column(String)
        image_url = Column(String)

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
            lazy='joined',
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

        @classmethod  # type: ignore
        @property
        def columns(cls) -> Tuple[ColumnProperty, ...]:
            inspector = schema_inspect(cls)
            return tuple(inspector.mapper.column_attrs)

        @property
        def entity_key(self) -> EntityKey:
            """
            This method returns the "external" key of an entity.
            """
            return str(self.external_id), str(self.plugin)

        def copy(self) -> 'Entity':
            """
            This method returns a copy of the entity. It's useful when you want
            to reuse entity objects in other threads or outside of their
            associated SQLAlchemy session context.
            """
            return self.__class__(
                **{col.key: getattr(self, col.key, None) for col in self.columns},
                children=[child.copy() for child in self.children],
            )

        def _serialize_value(self, column_name: str) -> Any:
            val = getattr(self, column_name)
            if isinstance(val, datetime):
                # All entity timestamps are in UTC
                val = val.replace(tzinfo=tzutc()).isoformat()

            return val

        def _column_name(self, col: ColumnProperty) -> str:
            """
            Normalizes the column name, taking into account native columns and
            columns mapped to properties.
            """
            normalized_name = col.key.lstrip('_')
            if len(col.key.lstrip('_')) == col.key or not hasattr(
                self, normalized_name
            ):
                return col.key  # It's not a hidden column with a mapped property

            return normalized_name

        def _column_to_pair(self, col: ColumnProperty) -> Tuple[str, Any]:
            """
            Utility method that, given a column, returns a pair containing its
            normalized name and its serialized value.
            """
            col_name = self._column_name(col)
            return col_name, self._serialize_value(col_name)

        def to_dict(self) -> dict:
            """
            Returns the current entity as a flatten dictionary.
            """
            return dict(self._column_to_pair(col) for col in self.columns)

        def to_json(self) -> dict:
            """
            Alias for :meth:`.to_dict`.
            """
            return self.to_dict()

        def __repr__(self):
            """
            Same as :meth:`.__str__`.
            """
            return str(self)

        def __str__(self):
            """
            :return: A JSON-encoded representation of the entity.
            """
            return json.dumps(self.to_dict(), cls=Message.Encoder)

        def __setattr__(self, key, value):
            """
            Serializes the new value before assigning it to an attribute.
            """
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

    EntitySavedCallback = Callable[[Entity], Any]
    """
    Type for the callback functions that should be called when an entity is saved
    on the database.
    """


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
            if (
                isinstance(e, (ImportError, ModuleNotFoundError))
                and modname[len(__package__) + 1 :] in _import_error_ignored_modules
            ):
                logger.debug(f'Could not import module {modname}')
            else:
                logger.warning(f'Could not import module {modname}')
                logger.exception(e)

            continue

        for _, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and issubclass(obj, Entity):
                entities_registry[obj] = {}


def get_entities_registry() -> EntityRegistryType:
    """
    :returns: A copy of the entities registry.
    """
    return entities_registry.copy()


def init_entities_db():
    """
    Initializes the entities database.
    """
    from platypush.context import get_plugin

    _discover_entity_types()
    db = get_plugin('db')
    assert db
    db.create_all(db.get_engine(), Base)
