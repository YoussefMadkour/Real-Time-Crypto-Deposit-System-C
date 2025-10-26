"""add block_time to blockchain_networks

Revision ID: 0003
Revises: 0002
Create Date: 2025-10-26 20:24:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0003'
down_revision = '0002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('blockchain_networks', sa.Column('block_time', sa.Integer(), nullable=True))
    # Set default value for existing records
    op.execute("UPDATE blockchain_networks SET block_time = 12")
    # Make it NOT NULL after setting defaults
    op.alter_column('blockchain_networks', 'block_time', nullable=False)


def downgrade() -> None:
    op.drop_column('blockchain_networks', 'block_time')

