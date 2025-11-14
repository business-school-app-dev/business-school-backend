"""merge heads

Revision ID: 839d29df77c5
Revises: 3da9ef3b1bcd, b8ebb9931ca1
Create Date: 2025-11-14 16:51:26.347402

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '839d29df77c5'
down_revision: Union[str, Sequence[str], None] = ('3da9ef3b1bcd', 'b8ebb9931ca1')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
