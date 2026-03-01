"""add admin_users table

Revision ID: a1b2c3d4e5f6
Revises: d0214321f5ed
Create Date: 2026-02-27 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'd0214321f5ed'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'admin_users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('username', sa.String(64), nullable=False),
        sa.Column('password_hash', sa.String(256), nullable=False),
    )
    op.create_index('ix_admin_users_username', 'admin_users', ['username'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_admin_users_username', table_name='admin_users')
    op.drop_table('admin_users')
