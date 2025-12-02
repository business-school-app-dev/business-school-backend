"""merge heads

Revision ID: 573f289caff3
Revises: 85b4a8a2c4a8
Create Date: 2025-11-28 02:00:52.219108

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '573f289caff3'
down_revision: Union[str, Sequence[str], None] = '85b4a8a2c4a8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
