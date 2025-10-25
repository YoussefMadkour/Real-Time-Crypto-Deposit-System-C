#!/usr/bin/env python3
"""
Database Initialization Script

This script initializes the database with sample blockchain network data.
Run this after running migrations to set up the initial data.
"""

import asyncio
import sys
from pathlib import Path
from uuid import uuid4

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent))

from app.database import AsyncSessionLocal
from app.models.user import BlockchainNetwork
from app.config import settings


async def init_database():
    """Initialize database with sample data."""
    async with AsyncSessionLocal() as db:
        # Check if Ethereum Sepolia network already exists
        from sqlalchemy import select
        result = await db.execute(
            select(BlockchainNetwork).where(BlockchainNetwork.chain_id == settings.chain_id)
        )
        existing_network = result.scalar_one_or_none()
        
        if existing_network:
            print(f"Blockchain network for chain ID {settings.chain_id} already exists")
            return
        
        # Create Ethereum Sepolia network
        sepolia_network = BlockchainNetwork(
            id=uuid4(),
            name="Ethereum Sepolia Testnet",
            chain_id=settings.chain_id,
            rpc_url=settings.alchemy_http_url,
            ws_url=settings.alchemy_ws_url,
            confirmations_required=settings.confirmations_required,
            is_active=True
        )
        
        db.add(sepolia_network)
        await db.commit()
        
        print(f"Created blockchain network: {sepolia_network.name}")
        print(f"Chain ID: {sepolia_network.chain_id}")
        print(f"Required confirmations: {sepolia_network.confirmations_required}")


if __name__ == "__main__":
    asyncio.run(init_database())
