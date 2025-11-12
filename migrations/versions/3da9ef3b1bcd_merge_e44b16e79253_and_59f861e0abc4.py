"""merge e44b16e79253 and 59f861e0abc4

Revision ID: 3da9ef3b1bcd
Revises: e44b16e79253, 59f861e0abc4
Create Date: 2025-11-09 23:46:49.099305

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3da9ef3b1bcd'
down_revision: Union[str, Sequence[str], None] = ('e44b16e79253', '59f861e0abc4')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
