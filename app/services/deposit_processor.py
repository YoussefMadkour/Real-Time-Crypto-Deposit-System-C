from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from decimal import Decimal
import logging

from app.models.user import Deposit, Wallet, BlockchainNetwork, DepositStatus
from app.schemas.deposit import DepositCreate, DepositUpdate
from app.utils import validate_transaction_hash, normalize_transaction_hash

logger = logging.getLogger(__name__)


class DepositProcessor:
    """Handles deposit processing logic and business rules."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_deposit(self, deposit_data: DepositCreate) -> Deposit:
        """Create a new deposit record."""
        # Validate transaction hash
        normalized_hash = normalize_transaction_hash(deposit_data.tx_hash)
        if not validate_transaction_hash(normalized_hash):
            raise ValueError("Invalid transaction hash format")
        
        # Check if deposit already exists
        existing_deposit = await self.get_deposit_by_tx_hash(normalized_hash)
        if existing_deposit:
            logger.warning(f"Deposit with tx_hash {normalized_hash} already exists")
            return existing_deposit
        
        # Validate wallet exists
        wallet = await self.get_wallet_by_id(deposit_data.wallet_id)
        if not wallet:
            raise ValueError("Wallet not found")
        
        # Validate blockchain network exists
        network = await self.get_network_by_id(deposit_data.blockchain_network_id)
        if not network:
            raise ValueError("Blockchain network not found")
        
        # Create deposit
        deposit = Deposit(
            wallet_id=deposit_data.wallet_id,
            tx_hash=normalized_hash,
            amount=deposit_data.amount,
            confirmations=deposit_data.confirmations,
            status=deposit_data.status,
            blockchain_network_id=deposit_data.blockchain_network_id,
            block_number=deposit_data.block_number,
            block_hash=deposit_data.block_hash,
            from_address=deposit_data.from_address
        )
        
        self.db.add(deposit)
        await self.db.commit()
        await self.db.refresh(deposit)
        
        logger.info(f"Created deposit {deposit.id} for tx_hash {normalized_hash}")
        return deposit
    
    async def update_deposit(self, deposit_id: str, update_data: DepositUpdate) -> Optional[Deposit]:
        """Update an existing deposit."""
        result = await self.db.execute(select(Deposit).where(Deposit.id == deposit_id))
        deposit = result.scalar_one_or_none()
        
        if not deposit:
            return None
        
        # Update fields
        if update_data.confirmations is not None:
            deposit.confirmations = update_data.confirmations
        
        if update_data.status is not None:
            deposit.status = update_data.status
        
        if update_data.block_number is not None:
            deposit.block_number = update_data.block_number
        
        if update_data.block_hash is not None:
            deposit.block_hash = update_data.block_hash
        
        await self.db.commit()
        await self.db.refresh(deposit)
        
        logger.info(f"Updated deposit {deposit.id}")
        return deposit
    
    async def update_deposit_confirmations(self, tx_hash: str, confirmations: int, block_hash: str = None) -> Optional[Deposit]:
        """Update deposit confirmations and determine status."""
        normalized_hash = normalize_transaction_hash(tx_hash)
        
        result = await self.db.execute(select(Deposit).where(Deposit.tx_hash == normalized_hash))
        deposit = result.scalar_one_or_none()
        
        if not deposit:
            return None
        
        # Update confirmations
        deposit.confirmations = confirmations
        
        if block_hash:
            deposit.block_hash = block_hash
        
        # Determine status based on confirmations
        network = await self.get_network_by_id(deposit.blockchain_network_id)
        required_confirmations = network.confirmations_required if network else 12
        
        if confirmations >= required_confirmations:
            deposit.status = DepositStatus.COMPLETED
        elif confirmations > 0:
            deposit.status = DepositStatus.CONFIRMING
        else:
            deposit.status = DepositStatus.PENDING
        
        await self.db.commit()
        await self.db.refresh(deposit)
        
        logger.info(f"Updated deposit {deposit.id} confirmations to {confirmations}, status: {deposit.status}")
        return deposit
    
    async def mark_deposit_orphaned(self, tx_hash: str) -> Optional[Deposit]:
        """Mark a deposit as orphaned due to blockchain reorg."""
        normalized_hash = normalize_transaction_hash(tx_hash)
        
        result = await self.db.execute(select(Deposit).where(Deposit.tx_hash == normalized_hash))
        deposit = result.scalar_one_or_none()
        
        if not deposit:
            return None
        
        deposit.status = DepositStatus.ORPHANED
        await self.db.commit()
        await self.db.refresh(deposit)
        
        logger.warning(f"Marked deposit {deposit.id} as orphaned")
        return deposit
    
    async def get_deposit_by_tx_hash(self, tx_hash: str) -> Optional[Deposit]:
        """Get deposit by transaction hash."""
        normalized_hash = normalize_transaction_hash(tx_hash)
        result = await self.db.execute(select(Deposit).where(Deposit.tx_hash == normalized_hash))
        return result.scalar_one_or_none()
    
    async def get_wallet_by_id(self, wallet_id: str) -> Optional[Wallet]:
        """Get wallet by ID."""
        result = await self.db.execute(select(Wallet).where(Wallet.id == wallet_id))
        return result.scalar_one_or_none()
    
    async def get_network_by_id(self, network_id: str) -> Optional[BlockchainNetwork]:
        """Get blockchain network by ID."""
        result = await self.db.execute(select(BlockchainNetwork).where(BlockchainNetwork.id == network_id))
        return result.scalar_one_or_none()
    
    async def get_monitored_wallets(self) -> List[Wallet]:
        """Get all active wallets that should be monitored."""
        result = await self.db.execute(
            select(Wallet)
            .where(Wallet.is_active == True)
            .join(BlockchainNetwork)
            .where(BlockchainNetwork.is_active == True)
        )
        return result.scalars().all()
