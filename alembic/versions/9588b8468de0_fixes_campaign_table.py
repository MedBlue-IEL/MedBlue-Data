"""fixes_campaign_table

Revision ID: 9588b8468de0
Revises: 3b51a1043dfc
Create Date: 2026-11-05 18:35:04.099366

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

import sqlmodel

# revision identifiers, used by Alembic.
revision: str = '9588b8468de0'
down_revision: Union[str, Sequence[str], None] = '3b51a1043dfc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
