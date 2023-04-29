"""Migrate variable table

Revision ID: c39ac404119b
Revises: d030953a871d
Create Date: 2023-04-28 22:35:28.307954

"""

import sqlalchemy as sa
from alembic import op

from platypush.entities import Entity

# revision identifiers, used by Alembic.
revision = 'c39ac404119b'
down_revision = 'd030953a871d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Get the connection and the existing `variable` table
    conn = op.get_bind()
    metadata = sa.MetaData()
    metadata.reflect(bind=conn)
    VariableOld = metadata.tables.get('variable')

    if VariableOld is None:
        print('The table `variable` does not exist, skipping migration')
        return

    # Create the `variable_new` table
    VariableNew = op.create_table(
        'variable_new',
        sa.Column(
            'id',
            sa.Integer,
            sa.ForeignKey(Entity.id, ondelete='CASCADE'),
            primary_key=True,
        ),
        sa.Column('value', sa.String),
    )

    assert VariableNew is not None, 'Could not create table "variable_new"'

    # Select all existing variables
    existing_vars = {
        var.name: var.value for var in conn.execute(sa.select(VariableOld)).all()
    }

    # Insert all the existing variables as entities
    if existing_vars:
        conn.execute(
            sa.insert(Entity).values(
                [
                    {
                        'external_id': name,
                        'name': name,
                        'type': 'variable',
                        'plugin': 'variable',
                    }
                    for name in existing_vars
                ]
            )
        )

        # Fetch all the newly inserted variables
        new_vars = {
            entity.id: entity.name
            for entity in conn.execute(
                sa.select(Entity.id, Entity.name).where(
                    sa.or_(
                        *[
                            sa.and_(
                                Entity.external_id == name,
                                Entity.type == 'variable',
                                Entity.plugin == 'variable',
                            )
                            for name in existing_vars
                        ]
                    )
                )
            ).all()
        }

        # Insert the mapping on the `variable_new` table
        op.bulk_insert(
            VariableNew,
            [
                {
                    'id': id,
                    'value': existing_vars.get(name),
                }
                for id, name in new_vars.items()
            ],
        )

    # Rename/drop the tables
    op.rename_table('variable', 'variable_old')
    op.rename_table('variable_new', 'variable')
    op.drop_table('variable_old')


def downgrade() -> None:
    # Get the connection and the existing `variable` table
    conn = op.get_bind()
    metadata = sa.MetaData()
    metadata.reflect(bind=conn)
    VariableNew = metadata.tables['variable']

    if VariableNew is None:
        print('The table `variable` does not exist, skipping migration')
        return

    # Create the `variable_old` table
    VariableOld = op.create_table(
        'variable_old',
        sa.Column('name', sa.String, primary_key=True, nullable=False),
        sa.Column('value', sa.String),
    )

    assert VariableOld is not None, 'Could not create table "variable_old"'

    # Select all existing variables
    existing_vars = {
        var.name: var.value
        for var in conn.execute(
            sa.select(Entity.name, VariableNew.c.value).join(
                Entity, Entity.id == VariableNew.c.id
            )
        ).all()
    }

    # Insert the mapping on the `variable_old` table
    if existing_vars:
        op.bulk_insert(
            VariableOld,
            [
                {
                    'name': name,
                    'value': value,
                }
                for name, value in existing_vars.items()
            ],
        )

    # Delete existing references on the `entity` table
    conn.execute(sa.delete(Entity).where(Entity.type == 'variable'))

    # Rename/drop the tables
    op.rename_table('variable', 'variable_new')
    op.rename_table('variable_old', 'variable')
    op.drop_table('variable_new')
