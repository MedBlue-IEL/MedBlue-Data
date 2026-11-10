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
    """Upgrade schema.

    Drop the old unique index on campaign_code (created in 2bb8f3776c85) so that
    b08d3abf7396 can recreate it; otherwise upgrade fails with DuplicateTable.
    """
    op.execute("DROP INDEX IF EXISTS ix_campaign_event_campaign_code")


def downgrade() -> None:
    """Downgrade schema."""
    op.create_index(op.f('ix_campaign_event_campaign_code'), 'campaign_event', ['campaign_code'], unique=True)
