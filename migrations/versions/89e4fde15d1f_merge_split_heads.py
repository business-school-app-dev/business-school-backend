"""Merge split heads

Revision ID: 89e4fde15d1f
Revises: 85b4a8a2c4a8, 8606916fd656
Create Date: 2025-11-27 14:41:53.419887

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '89e4fde15d1f'
down_revision: Union[str, Sequence[str], None] = ('85b4a8a2c4a8', '8606916fd656')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
