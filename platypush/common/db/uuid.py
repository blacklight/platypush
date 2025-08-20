import uuid

from sqlalchemy.types import TypeDecorator, CHAR, BINARY
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

try:
    # SQLAlchemy >= 2.0
    from sqlalchemy import UUID  # type:ignore[import-not-found]
except Exception:
    # SQLAlchemy < 2.0
    class UUID(TypeDecorator):
        """
        Platform-independent UUID type.
        Uses PostgreSQL's UUID type, otherwise stores as stringified hex.
        """

        impl = CHAR

        def load_dialect_impl(self, dialect):
            # PostgreSQL has native UUID
            if dialect.name == 'postgresql':
                return dialect.type_descriptor(PG_UUID())
            # MySQL can use BINARY(16)
            elif dialect.name == 'mysql':
                return dialect.type_descriptor(BINARY(16))
            # SQLite and others use CHAR(32)
            else:
                return dialect.type_descriptor(CHAR(32))

        def process_bind_param(self, value, dialect):
            if value is None:
                return value
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(str(value))

            if dialect.name == 'postgresql':
                return str(value)
            elif dialect.name == 'mysql':
                return value.bytes
            else:
                # SQLite, others: store as hex string
                return value.hex

        def process_result_value(self, value, dialect):
            if value is None:
                return value
            if dialect.name == 'mysql':
                return uuid.UUID(bytes=value)
            else:
                return uuid.UUID(str(value))


__all__ = ('UUID',)
