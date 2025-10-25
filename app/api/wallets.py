from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from app.database import get_db
from app.models.user import User, Wallet, BlockchainNetwork
from app.schemas.wallet import WalletCreate, WalletResponse
from app.utils import is_valid_ethereum_address, normalize_address

router = APIRouter()


@router.post("/", response_model=WalletResponse, status_code=status.HTTP_201_CREATED)
async def create_wallet(
    wallet_data: WalletCreate,
    db: AsyncSession = Depends(get_db)
):
    """Add a wallet to a user."""
    # Validate user exists
    result = await db.execute(select(User).where(User.id == wallet_data.user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Validate blockchain network exists
    result = await db.execute(select(BlockchainNetwork).where(BlockchainNetwork.id == wallet_data.blockchain_network_id))
    network = result.scalar_one_or_none()
    
    if not network:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blockchain network not found"
        )
    
    # Validate address format
    if not is_valid_ethereum_address(wallet_data.address):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Ethereum address format"
        )
    
    # Check if wallet already exists
    normalized_address = normalize_address(wallet_data.address)
    result = await db.execute(select(Wallet).where(Wallet.address == normalized_address))
    existing_wallet = result.scalar_one_or_none()
    
    if existing_wallet:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wallet address already exists"
        )
    
    # Create new wallet
    wallet = Wallet(
        user_id=wallet_data.user_id,
        address=normalized_address,
        blockchain_network_id=wallet_data.blockchain_network_id,
        label=wallet_data.label,
        is_active=wallet_data.is_active
    )
    
    db.add(wallet)
    await db.commit()
    await db.refresh(wallet)
    
    return wallet


@router.get("/{wallet_id}", response_model=WalletResponse)
async def get_wallet(
    wallet_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get wallet by ID."""
    result = await db.execute(select(Wallet).where(Wallet.id == wallet_id))
    wallet = result.scalar_one_or_none()
    
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found"
        )
    
    return wallet


@router.get("/user/{user_id}", response_model=List[WalletResponse])
async def get_user_wallets(
    user_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get all wallets for a user."""
    result = await db.execute(select(Wallet).where(Wallet.user_id == user_id))
    wallets = result.scalars().all()
    
    return wallets


@router.get("/address/{address}", response_model=WalletResponse)
async def get_wallet_by_address(
    address: str,
    db: AsyncSession = Depends(get_db)
):
    """Get wallet by address."""
    normalized_address = normalize_address(address)
    
    if not is_valid_ethereum_address(normalized_address):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Ethereum address format"
        )
    
    result = await db.execute(select(Wallet).where(Wallet.address == normalized_address))
    wallet = result.scalar_one_or_none()
    
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found"
        )
    
    return wallet
