"""Initial migration

Revision ID: 0001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create blockchain_networks table
    op.create_table('blockchain_networks',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('chain_id', sa.Integer(), nullable=False),
    sa.Column('rpc_url', sa.String(), nullable=False),
    sa.Column('ws_url', sa.String(), nullable=False),
    sa.Column('confirmations_required', sa.Integer(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_blockchain_networks_chain_id'), 'blockchain_networks', ['chain_id'], unique=False)

    # Create users table
    op.create_table('users',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # Create wallets table
    op.create_table('wallets',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('address', sa.String(), nullable=False),
    sa.Column('blockchain_network_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('label', sa.String(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['blockchain_network_id'], ['blockchain_networks.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_wallets_address'), 'wallets', ['address'], unique=True)
    op.create_index(op.f('ix_wallets_user_id'), 'wallets', ['user_id'], unique=False)

    # Create deposits table
    op.create_table('deposits',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('wallet_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('tx_hash', sa.String(), nullable=False),
    sa.Column('amount', sa.Numeric(precision=36, scale=18), nullable=False),
    sa.Column('confirmations', sa.Integer(), nullable=False),
    sa.Column('status', sa.Enum('pending', 'confirming', 'completed', 'failed', 'orphaned', name='depositstatus'), nullable=False),
    sa.Column('blockchain_network_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('block_number', sa.BigInteger(), nullable=True),
    sa.Column('block_hash', sa.String(), nullable=True),
    sa.Column('from_address', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['blockchain_network_id'], ['blockchain_networks.id'], ),
    sa.ForeignKeyConstraint(['wallet_id'], ['wallets.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_deposits_tx_hash'), 'deposits', ['tx_hash'], unique=True)
    op.create_index(op.f('ix_deposits_wallet_id'), 'deposits', ['wallet_id'], unique=False)
    op.create_index(op.f('ix_deposits_status'), 'deposits', ['status'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_deposits_status'), table_name='deposits')
    op.drop_index(op.f('ix_deposits_wallet_id'), table_name='deposits')
    op.drop_index(op.f('ix_deposits_tx_hash'), table_name='deposits')
    op.drop_table('deposits')
    op.drop_index(op.f('ix_wallets_user_id'), table_name='wallets')
    op.drop_index(op.f('ix_wallets_address'), table_name='wallets')
    op.drop_table('wallets')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_blockchain_networks_chain_id'), table_name='blockchain_networks')
    op.drop_table('blockchain_networks')
    op.execute('DROP TYPE depositstatus')
