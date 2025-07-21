from contextlib import contextmanager
from dataclasses import dataclass

from sqlalchemy.orm import declarative_base

from .uuid import UUID

Base = declarative_base()


@dataclass
class DbContext:
    """
    Context flags for the database session.
    """

    override_definitions: bool = False


_ctx = DbContext()


@contextmanager
def override_definitions():
    """
    Temporarily override the definitions of the entities in the entities
    registry.

    This is useful when the entities are being imported off-context, like
    e.g. in the `inspect` or `alembic` modules.
    """
    _ctx.override_definitions = True
    yield
    _ctx.override_definitions = False


def is_defined(table_name: str) -> bool:
    """
    Check if the given entity class is defined in the entities registry.

    :param table_name: Name of the table associated to the entity class.
    """
    return not _ctx.override_definitions and table_name in Base.metadata


__all__ = [
    "DbContext",
    "UUID",
    "override_definitions",
    "is_defined",
]
