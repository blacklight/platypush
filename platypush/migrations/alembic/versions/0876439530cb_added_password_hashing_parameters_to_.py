"""Added password hashing parameters to user table

Revision ID: 0876439530cb
Revises: c39ac404119b
Create Date: 2024-05-05 20:57:02.820575

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0876439530cb'
down_revision = 'c39ac404119b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    metadata = sa.MetaData()
    metadata.reflect(bind=conn)
    user_table = metadata.tables.get('user')

    if user_table is None:
        print('The table `user` does not exist, skipping migration')
        return

    if 'password_salt' not in user_table.columns:
        op.add_column('user', sa.Column('password_salt', sa.String(), nullable=True))

    if 'hmac_iterations' not in user_table.columns:
        op.add_column('user', sa.Column('hmac_iterations', sa.Integer(), nullable=True))


def downgrade() -> None:
    conn = op.get_bind()
    metadata = sa.MetaData()
    metadata.reflect(bind=conn)
    user_table = metadata.tables.get('user')

    if user_table is None:
        print('The table `user` does not exist, skipping migration')
        return

    if 'password_salt' in user_table.columns:
        op.drop_column('user', 'password_salt')

    if 'hmac_iterations' in user_table.columns:
        op.drop_column('user', 'hmac_iterations')
