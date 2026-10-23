"""add_habitat_array_validation_trigger

Revision ID: 3b51a1043dfc
Revises: 8e19473b9263
Create Date: 2026-10-22 18:29:40.190807

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

import sqlmodel

# revision identifiers, used by Alembic.
revision: str = '3b51a1043dfc'
down_revision: Union[str, Sequence[str], None] = '8e19473b9263'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create the PL/pgSQL validation trigger function
    op.execute("""
        CREATE OR REPLACE FUNCTION validate_campaign_habitat_ids()
        RETURNS TRIGGER AS $$
        DECLARE
            valid_count INT;
            array_count INT;
        BEGIN
            -- Count unique, non-null elements in the array
            SELECT COUNT(DISTINCT val)
            INTO array_count
            FROM unnest(NEW.habitat_ids) AS val
            WHERE val IS NOT NULL;

            -- Count how many of those IDs exist in the habitat table
            SELECT COUNT(*)
            INTO valid_count
            FROM habitat
            WHERE id = ANY(NEW.habitat_ids);

            -- Block operation if counts mismatch
            IF array_count <> valid_count THEN
                RAISE EXCEPTION 'Referential integrity violation: One or more IDs in habitat_ids do not exist in the habitat table.';
            END IF;

            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # 2. Attach the trigger to the campaign_event table
    op.execute("""
        CREATE TRIGGER check_campaign_habitat_ids
        BEFORE INSERT OR UPDATE ON campaign_event
        FOR EACH ROW
        EXECUTE FUNCTION validate_campaign_habitat_ids();
    """)


def downgrade() -> None:
    # Safely tear down trigger and function if rolling back migrations
    op.execute("DROP TRIGGER IF EXISTS check_campaign_habitat_ids ON campaign_event;")
    op.execute("DROP FUNCTION IF EXISTS validate_campaign_habitat_ids();")
