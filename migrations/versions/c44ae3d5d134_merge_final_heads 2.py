"""merge final heads

Revision ID: c44ae3d5d134
Revises: 573f289caff3, dc284f36fe7d
Create Date: 2025-11-28 02:02:16.357068

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c44ae3d5d134'
down_revision: Union[str, Sequence[str], None] = ('573f289caff3', 'dc284f36fe7d')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
