"""Drop projects table

Revision ID: d0214321f5ed
Revises: 7085c0c5e405
Create Date: 2025-12-10 18:21:04.549040

"""
from typing import Sequence, Union

from alembic import op
# import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd0214321f5ed'
down_revision: Union[str, Sequence[str], None] = '7085c0c5e405'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_table("project_tags")
    op.drop_table("projects")


def downgrade() -> None:
    """Downgrade schema."""
    pass
