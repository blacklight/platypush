import inspect
import pathlib
from datetime import datetime
from typing import Mapping, Type

import pkgutil
from sqlalchemy import Column, Index, Integer, String, DateTime, JSON, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
entities_registry: Mapping[Type['Entity'], Mapping] = {}


class Entity(Base):
    """
    Model for a general-purpose platform entity
    """

    __tablename__ = 'entity'

    id = Column(Integer, autoincrement=True, primary_key=True)
    external_id = Column(String, nullable=True)
    name = Column(String, nullable=False, index=True)
    type = Column(String, nullable=False, index=True)
    plugin = Column(String, nullable=False)
    data = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=False), default=datetime.utcnow(), nullable=False)
    updated_at = Column(DateTime(timezone=False), default=datetime.utcnow(), onupdate=datetime.now())

    UniqueConstraint(external_id, plugin)

    __table_args__ = (
        Index(name, plugin),
    )

    __mapper_args__ = {
        'polymorphic_identity': __tablename__,
        'polymorphic_on': type,
    }


def _discover_entity_types():
    from platypush.context import get_plugin
    logger = get_plugin('logger')
    assert logger

    for loader, modname, _ in pkgutil.walk_packages(
        path=[str(pathlib.Path(__file__).parent.absolute())],
        prefix=__package__ + '.',
        onerror=lambda _: None
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


def init_entities_db():
    from platypush.context import get_plugin
    _discover_entity_types()
    db = get_plugin('db')
    assert db
    engine = db.get_engine()
    db.create_all(engine, Base)

