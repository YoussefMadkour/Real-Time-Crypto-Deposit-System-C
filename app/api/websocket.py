from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, List
import json
import logging

from app.database import get_db
from app.models.user import Wallet
from app.schemas.deposit import DepositEvent, ConfirmationUpdateEvent
from app.utils import is_valid_ethereum_address, normalize_address
from app.services.websocket_manager import WebSocketManager

router = APIRouter()
logger = logging.getLogger(__name__)

# Global WebSocket manager instance
websocket_manager = WebSocketManager()


@router.websocket("/")
async def websocket_endpoint(
    websocket: WebSocket,
    wallet_address: str = Query(..., description="Wallet address to monitor")
):
    """
    WebSocket endpoint for real-time deposit updates.
    
    Connect with: ws://localhost:8000/ws/?wallet_address=0x...
    """
    # Validate wallet address
    normalized_address = normalize_address(wallet_address)
    
    if not is_valid_ethereum_address(normalized_address):
        await websocket.close(code=4000, reason="Invalid wallet address format")
        return
    
    # Accept the connection
    await websocket.accept()
    
    try:
        # Register the connection
        await websocket_manager.connect(websocket, normalized_address)
        logger.info(f"WebSocket connected for wallet: {normalized_address}")
        
        # Send welcome message
        await websocket.send_text(json.dumps({
            "type": "connected",
            "message": f"Connected to updates for wallet {normalized_address}",
            "wallet_address": normalized_address
        }))
        
        # Keep the connection alive
        while True:
            try:
                # Wait for ping from client
                data = await websocket.receive_text()
                if data == "ping":
                    await websocket.send_text("pong")
            except WebSocketDisconnect:
                break
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for wallet: {normalized_address}")
    except Exception as e:
        logger.error(f"WebSocket error for wallet {normalized_address}: {e}")
    finally:
        # Unregister the connection
        await websocket_manager.disconnect(websocket, normalized_address)


@router.get("/connections")
async def get_active_connections():
    """Get information about active WebSocket connections."""
    return {
        "active_connections": websocket_manager.get_connection_count(),
        "monitored_wallets": list(websocket_manager.get_monitored_wallets())
    }
