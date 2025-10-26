from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from app.database import get_db
from app.models.user import BlockchainNetwork
from app.schemas.blockchain_network import (
    BlockchainNetworkCreate,
    BlockchainNetworkResponse,
    BlockchainNetworkUpdate,
)

router = APIRouter()


@router.post("/", response_model=BlockchainNetworkResponse, status_code=status.HTTP_201_CREATED)
async def create_blockchain_network(
    network_data: BlockchainNetworkCreate, db: AsyncSession = Depends(get_db)
):
    """Create a new blockchain network."""
    # Check if network with same chain_id already exists
    result = await db.execute(
        select(BlockchainNetwork).where(BlockchainNetwork.chain_id == network_data.chain_id)
    )
    existing_network = result.scalar_one_or_none()

    if existing_network:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Blockchain network with this chain ID already exists",
        )

    # Create new network
    network = BlockchainNetwork(
        name=network_data.name,
        chain_id=network_data.chain_id,
        rpc_url=network_data.rpc_url,
        ws_url=network_data.ws_url,
        confirmations_required=network_data.confirmations_required,
        is_active=network_data.is_active,
    )
    db.add(network)
    await db.commit()
    await db.refresh(network)

    return network


@router.get("/", response_model=List[BlockchainNetworkResponse])
async def list_blockchain_networks(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    """List all blockchain networks."""
    result = await db.execute(
        select(BlockchainNetwork).offset(skip).limit(limit).order_by(BlockchainNetwork.created_at)
    )
    networks = result.scalars().all()

    return networks


@router.get("/{network_id}", response_model=BlockchainNetworkResponse)
async def get_blockchain_network(
    network_id: UUID, db: AsyncSession = Depends(get_db)
):
    """Get blockchain network by ID."""
    result = await db.execute(
        select(BlockchainNetwork).where(BlockchainNetwork.id == network_id)
    )
    network = result.scalar_one_or_none()

    if not network:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Blockchain network not found"
        )

    return network


@router.put("/{network_id}", response_model=BlockchainNetworkResponse)
async def update_blockchain_network(
    network_id: UUID,
    network_data: BlockchainNetworkUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update an existing blockchain network."""
    # Get the network
    result = await db.execute(
        select(BlockchainNetwork).where(BlockchainNetwork.id == network_id)
    )
    network = result.scalar_one_or_none()

    if not network:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Blockchain network not found"
        )

    # Check if chain_id is being updated and if it's already taken
    if network_data.chain_id and network_data.chain_id != network.chain_id:
        result = await db.execute(
            select(BlockchainNetwork).where(BlockchainNetwork.chain_id == network_data.chain_id)
        )
        existing_network = result.scalar_one_or_none()

        if existing_network:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Blockchain network with this chain ID already exists",
            )
        network.chain_id = network_data.chain_id

    # Update other fields if provided
    if network_data.name is not None:
        network.name = network_data.name

    if network_data.rpc_url is not None:
        network.rpc_url = network_data.rpc_url

    if network_data.ws_url is not None:
        network.ws_url = network_data.ws_url

    if network_data.confirmations_required is not None:
        network.confirmations_required = network_data.confirmations_required

    if network_data.is_active is not None:
        network.is_active = network_data.is_active

    await db.commit()
    await db.refresh(network)

    return network


@router.delete("/{network_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_blockchain_network(
    network_id: UUID, db: AsyncSession = Depends(get_db)
):
    """Delete a blockchain network."""
    result = await db.execute(
        select(BlockchainNetwork).where(BlockchainNetwork.id == network_id)
    )
    network = result.scalar_one_or_none()

    if not network:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Blockchain network not found"
        )

    await db.delete(network)
    await db.commit()

    return None
