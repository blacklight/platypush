"""Added notes_content_index table

Revision ID: 99b960c6cb8c
Revises: 692bc6eb9c81
Create Date: 2025-06-23 00:22:30.278210

"""

from alembic import op
import sqlalchemy as sa

from platypush.plugins._notes.db._model import (
    Note as DbNote,
    NoteContentIndex as DbNoteContentIndex,
)


# revision identifiers, used by Alembic.
revision = '99b960c6cb8c'
down_revision = '692bc6eb9c81'
branch_labels = None
depends_on = None


def _create_note_content_index_table(metadata: sa.MetaData) -> sa.Table:
    table_name = DbNoteContentIndex.__tablename__
    existing_table = metadata.tables.get(table_name)
    if existing_table is not None:
        print(f'Table `{table_name}` already exists, skipping creation')
        return existing_table

    return op.create_table(
        table_name,
        sa.Column(
            'note_id',
            sa.UUID,
            sa.ForeignKey(f'{DbNote.__tablename__}.id', ondelete='CASCADE'),
            nullable=False,
        ),
        sa.Column('token', sa.String, nullable=False, index=True),
        sa.Column('length', sa.Integer, nullable=False),
        sa.Column('count', sa.Integer, nullable=False, default=1),
        sa.PrimaryKeyConstraint('note_id', 'token', name=f'{table_name}_pkey'),
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
    _create_note_content_index_table(metadata)


def downgrade() -> None:
    conn = op.get_bind()
    metadata = sa.MetaData()
    metadata.reflect(bind=conn)
    _drop_table_if_exists(DbNoteContentIndex.__tablename__, metadata)
