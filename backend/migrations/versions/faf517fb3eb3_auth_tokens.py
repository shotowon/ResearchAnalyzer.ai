"""auth tokens

Revision ID: faf517fb3eb3
Revises: 70f030eae5cb
Create Date: 2025-05-18 23:17:40.423496

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "faf517fb3eb3"
down_revision: Union[str, None] = "70f030eae5cb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "auth_tokens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("token", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user_accounts.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("auth_tokens")
    pass
