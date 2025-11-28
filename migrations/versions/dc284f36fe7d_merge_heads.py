"""merge heads

Revision ID: dc284f36fe7d
Revises: 8606916fd656
Create Date: 2025-11-28 02:01:04.738002

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dc284f36fe7d'
down_revision: Union[str, Sequence[str], None] = '8606916fd656'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
