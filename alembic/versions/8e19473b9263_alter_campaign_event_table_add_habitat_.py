"""alter_campaign_event_table_add_habitat_array_validation_trigger

Revision ID: 8e19473b9263
Revises: ac45ca4dff61
Create Date: 2026-10-22 18:10:18.410310

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

import sqlmodel

# revision identifiers, used by Alembic.
revision: str = '8e19473b9263'
down_revision: Union[str, Sequence[str], None] = 'ac45ca4dff61'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
