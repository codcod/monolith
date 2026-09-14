"""create dispatcher schema

Revision ID: 057e6b8a161e
Revises:
Create Date: 2026-09-13 13:30:52.223526

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '057e6b8a161e'
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute('CREATE SCHEMA IF NOT EXISTS dispatcher')
    op.create_table(
        'messages',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('channel', sa.Text(), nullable=False),
        sa.Column('recipient', sa.Text(), nullable=False),
        sa.Column('send_status', sa.Text(), nullable=False),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        schema='dispatcher',
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Not dropping the dispatcher schema itself: alembic's own version
    # table (version_table_schema="dispatcher", see stelo.base.migrations)
    # lives in it and alembic still needs it to record this downgrade.
    op.drop_table('messages', schema='dispatcher')
