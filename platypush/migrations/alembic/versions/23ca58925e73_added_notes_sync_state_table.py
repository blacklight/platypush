"""Added notes_sync_state table

Revision ID: 23ca58925e73
Revises: 99b960c6cb8c
Create Date: 2025-08-21 21:33:31.407142

"""

from alembic import op
import sqlalchemy as sa

from platypush.common.db import UUID
from platypush.plugins.notes.db._model import (
    Note as DbNote,
    NoteSyncState as DbNoteSyncState,
)

# revision identifiers, used by Alembic.
revision = '23ca58925e73'
down_revision = '99b960c6cb8c'
branch_labels = None
depends_on = None


def _create_notes_sync_state_table(metadata: sa.MetaData) -> sa.Table:
    table_name = DbNoteSyncState.__tablename__
    existing_table = metadata.tables.get(table_name)
    if existing_table is not None:
        print(f'Table `{table_name}` already exists, skipping creation')
        return existing_table

    return op.create_table(
        table_name,
        sa.Column(
            'local_note_id',
            UUID,
            sa.ForeignKey(f'{DbNote.__tablename__}.id', ondelete='CASCADE'),
            nullable=False,
        ),
        sa.Column(
            'remote_note_id',
            UUID,
            sa.ForeignKey(f'{DbNote.__tablename__}.id', ondelete='CASCADE'),
            nullable=False,
        ),
        sa.Column(
            'conflict_note_id',
            UUID,
            sa.ForeignKey(f'{DbNote.__tablename__}.id', ondelete='SET NULL'),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint(
            'local_note_id', 'remote_note_id', name=f'{table_name}_pkey'
        ),
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
    _create_notes_sync_state_table(metadata)


def downgrade() -> None:
    conn = op.get_bind()
    metadata = sa.MetaData()
    metadata.reflect(bind=conn)
    _drop_table_if_exists(DbNoteSyncState.__tablename__, metadata)
