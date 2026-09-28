"""create traffic schema

Revision ID: e00649473d3f
Revises:
Create Date: 2026-09-13 13:30:51.702142

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'e00649473d3f'
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute('CREATE SCHEMA IF NOT EXISTS traffic')
    _ = op.create_table(
        'messages',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('channel', sa.Text(), nullable=False),
        sa.Column('recipient', sa.Text(), nullable=False),
        sa.Column('routed_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        schema='traffic',
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Not dropping the traffic schema itself: alembic's own version table
    # (version_table_schema="traffic", see monobase.migrations) lives in
    # it and alembic still needs it to record this downgrade.
    op.drop_table('messages', schema='traffic')
