"""merging heads again

Revision ID: 32f6062af95a
Revises: 89e4fde15d1f, c44ae3d5d134
Create Date: 2025-11-28 02:13:08.576718

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '32f6062af95a'
down_revision: Union[str, Sequence[str], None] = ('89e4fde15d1f', 'c44ae3d5d134')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
