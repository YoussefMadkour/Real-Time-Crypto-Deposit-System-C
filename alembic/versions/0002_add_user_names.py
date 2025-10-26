"""Add first_name and last_name to users

Revision ID: 0002
Revises: 0001
Create Date: 2024-01-02 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add first_name and last_name columns to users table
    op.add_column("users", sa.Column("first_name", sa.String(), nullable=True))
    op.add_column("users", sa.Column("last_name", sa.String(), nullable=True))

    # Update existing users with default values if any exist
    op.execute("UPDATE users SET first_name = 'Unknown' WHERE first_name IS NULL")
    op.execute("UPDATE users SET last_name = 'User' WHERE last_name IS NULL")

    # Make columns non-nullable after setting default values
    op.alter_column("users", "first_name", nullable=False)
    op.alter_column("users", "last_name", nullable=False)


def downgrade() -> None:
    # Remove first_name and last_name columns from users table
    op.drop_column("users", "last_name")
    op.drop_column("users", "first_name")
