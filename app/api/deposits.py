from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from app.database import get_db
from app.models.user import Deposit, Wallet
from app.schemas.deposit import DepositResponse
from app.utils import validate_transaction_hash, normalize_transaction_hash

router = APIRouter()


@router.get("/wallet/{wallet_id}", response_model=List[DepositResponse])
async def get_wallet_deposits(
    wallet_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get deposits for a specific wallet."""
    # Validate wallet exists
    result = await db.execute(select(Wallet).where(Wallet.id == wallet_id))
    wallet = result.scalar_one_or_none()
    
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found"
        )
    
    # Get deposits
    result = await db.execute(
        select(Deposit)
        .where(Deposit.wallet_id == wallet_id)
        .order_by(Deposit.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    deposits = result.scalars().all()
    
    return deposits


@router.get("/{deposit_id}", response_model=DepositResponse)
async def get_deposit(
    deposit_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get deposit by ID."""
    result = await db.execute(select(Deposit).where(Deposit.id == deposit_id))
    deposit = result.scalar_one_or_none()
    
    if not deposit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deposit not found"
        )
    
    return deposit


@router.get("/tx/{tx_hash}", response_model=DepositResponse)
async def get_deposit_by_tx_hash(
    tx_hash: str,
    db: AsyncSession = Depends(get_db)
):
    """Get deposit by transaction hash."""
    normalized_hash = normalize_transaction_hash(tx_hash)
    
    if not validate_transaction_hash(normalized_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid transaction hash format"
        )
    
    result = await db.execute(select(Deposit).where(Deposit.tx_hash == normalized_hash))
    deposit = result.scalar_one_or_none()
    
    if not deposit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deposit not found"
        )
    
    return deposit


@router.get("/", response_model=List[DepositResponse])
async def list_deposits(
    skip: int = 0,
    limit: int = 100,
    status_filter: str = None,
    db: AsyncSession = Depends(get_db)
):
    """List all deposits with optional status filter."""
    query = select(Deposit).order_by(Deposit.created_at.desc())
    
    if status_filter:
        query = query.where(Deposit.status == status_filter)
    
    result = await db.execute(query.offset(skip).limit(limit))
    deposits = result.scalars().all()
    
    return deposits
