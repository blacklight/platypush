"""Added tables for note plugins

Revision ID: 692bc6eb9c81
Revises: 0876439530cb
Create Date: 2025-06-20 12:27:54.533624

"""

from alembic import op
import sqlalchemy as sa

from platypush.common.db import UUID
from platypush.plugins._notes.db._model import (
    Note as DbNote,
    NoteCollection as DbNoteCollection,
    NoteNoteResource as DbNoteNoteResource,
    NoteResource as DbNoteResource,
    NoteTag as DbNoteTag,
)


# revision identifiers, used by Alembic.
revision = '692bc6eb9c81'
down_revision = '0876439530cb'
branch_labels = None
depends_on = None


def _create_note_collection_table(metadata: sa.MetaData) -> sa.Table:
    table_name = DbNoteCollection.__tablename__
    existing_table = metadata.tables.get(table_name)
    if existing_table is not None:
        print(f'Table `{table_name}` already exists, skipping creation')
        return existing_table

    table = op.create_table(
        table_name,
        sa.Column('id', UUID, primary_key=True),
        sa.Column('external_id', sa.String, nullable=False),
        sa.Column('plugin', sa.String, nullable=False),
        sa.Column('title', sa.String, nullable=False, index=True),
        sa.Column('description', sa.String, nullable=True, index=True),
        sa.Column(
            'parent_id',
            UUID,
            sa.ForeignKey(f'{table_name}.id', ondelete='CASCADE'),
            nullable=True,
        ),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False),
        sa.UniqueConstraint(
            'external_id', 'plugin', name='note_collection_external_id_plugin_idx'
        ),
    )

    return table


def _create_note_resource_table(metadata: sa.MetaData) -> sa.Table:
    table_name = DbNoteResource.__tablename__
    existing_table = metadata.tables.get(table_name)
    if existing_table is not None:
        print(f'Table `{table_name}` already exists, skipping creation')
        return existing_table

    table = op.create_table(
        table_name,
        sa.Column('id', UUID, primary_key=True),
        sa.Column('external_id', sa.String, nullable=False),
        sa.Column('plugin', sa.String, nullable=False),
        sa.Column('title', sa.String, nullable=False, index=True),
        sa.Column('filename', sa.String, nullable=False),
        sa.Column('content_type', sa.String, nullable=True),
        sa.Column('size', sa.Integer, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=True),
        sa.UniqueConstraint(
            'external_id', 'plugin', name='note_resource_external_id_plugin_idx'
        ),
    )

    return table


def _create_note_table(metadata: sa.MetaData) -> sa.Table:
    table_name = DbNote.__tablename__
    existing_table = metadata.tables.get(table_name)
    if existing_table is not None:
        print(f'Table `{table_name}` already exists, skipping creation')
        return existing_table

    table = op.create_table(
        table_name,
        sa.Column('id', UUID, primary_key=True),
        sa.Column('external_id', sa.String, nullable=False),
        sa.Column('plugin', sa.String, nullable=False),
        sa.Column('title', sa.String, nullable=False, index=True),
        sa.Column('description', sa.String, nullable=True, index=True),
        sa.Column('content', sa.String, nullable=True),
        sa.Column(
            'parent_id',
            UUID,
            sa.ForeignKey(f'{DbNoteCollection.__tablename__}.id', ondelete='CASCADE'),
            nullable=True,
        ),
        sa.Column('digest', sa.String, nullable=True, index=True),
        sa.Column('latitude', sa.Float, nullable=True),
        sa.Column('longitude', sa.Float, nullable=True),
        sa.Column('altitude', sa.Float, nullable=True),
        sa.Column('author', sa.String, nullable=True),
        sa.Column('source_name', sa.String, nullable=True, index=True),
        sa.Column('source_url', sa.String, nullable=True, index=True),
        sa.Column('source_app', sa.String, nullable=True, index=True),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False),
        sa.UniqueConstraint(
            'external_id', 'plugin', name='note_external_id_plugin_idx'
        ),
    )

    return table


def _create_note_note_resource_table(metadata: sa.MetaData) -> sa.Table:
    table_name = DbNoteNoteResource.__tablename__
    existing_table = metadata.tables.get(table_name)
    if existing_table is not None:
        print(f'Table `{table_name}` already exists, skipping creation')
        return existing_table

    return op.create_table(
        table_name,
        sa.Column(
            'note_id',
            UUID,
            sa.ForeignKey(f'{DbNote.__tablename__}.id', ondelete='CASCADE'),
        ),
        sa.Column(
            'resource_id',
            sa.String,
            sa.ForeignKey(f'{DbNoteResource.__tablename__}.id', ondelete='CASCADE'),
        ),
        sa.PrimaryKeyConstraint('note_id', 'resource_id'),
    )


def _create_note_tag_table(metadata: sa.MetaData) -> sa.Table:
    table_name = DbNoteTag.__tablename__
    existing_table = metadata.tables.get(table_name)
    if existing_table is not None:
        print(f'Table `{table_name}` already exists, skipping creation')
        return existing_table

    return op.create_table(
        table_name,
        sa.Column(
            'note_id',
            UUID,
            sa.ForeignKey(f'{DbNote.__tablename__}.id'),
            nullable=False,
        ),
        sa.Column('tag', sa.String, nullable=False),
        sa.PrimaryKeyConstraint('note_id', 'tag', name='note_tag_pkey'),
    )


def _drop_table_if_exists(table_name: str, metadata: sa.MetaData) -> None:
    if table_name in metadata.tables:
        op.drop_table(table_name)
        print(f'Table `{table_name}` dropped successfully.')
    else:
        print(f'Table `{table_name}` does not exist, skipping drop.')


def upgrade() -> None:
    conn = op.get_bind()
    metadata = sa.MetaData()
    metadata.reflect(bind=conn)

    _create_note_collection_table(metadata)
    _create_note_resource_table(metadata)
    _create_note_table(metadata)
    _create_note_note_resource_table(metadata)
    _create_note_tag_table(metadata)


def downgrade() -> None:
    conn = op.get_bind()
    metadata = sa.MetaData()
    metadata.reflect(bind=conn)

    for table_name in [
        DbNoteTag.__tablename__,
        DbNoteNoteResource.__tablename__,
        DbNoteResource.__tablename__,
        DbNote.__tablename__,
        DbNoteCollection.__tablename__,
    ]:
        _drop_table_if_exists(table_name, metadata)
