from fastapi import WebSocket
from typing import Dict, List, Set
import json
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages WebSocket connections for real-time updates."""
    
    def __init__(self):
        # Map wallet addresses to sets of WebSocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = defaultdict(set)
        # Map WebSocket connections to wallet addresses
        self.connection_wallets: Dict[WebSocket, str] = {}
    
    async def connect(self, websocket: WebSocket, wallet_address: str):
        """Register a new WebSocket connection for a wallet."""
        self.active_connections[wallet_address].add(websocket)
        self.connection_wallets[websocket] = wallet_address
        logger.info(f"Connected WebSocket for wallet {wallet_address}")
    
    async def disconnect(self, websocket: WebSocket, wallet_address: str = None):
        """Unregister a WebSocket connection."""
        if websocket in self.connection_wallets:
            wallet_address = self.connection_wallets[websocket]
            del self.connection_wallets[websocket]
        
        if wallet_address and websocket in self.active_connections[wallet_address]:
            self.active_connections[wallet_address].discard(websocket)
            
            # Clean up empty sets
            if not self.active_connections[wallet_address]:
                del self.active_connections[wallet_address]
        
        logger.info(f"Disconnected WebSocket for wallet {wallet_address}")
    
    async def send_to_wallet(self, wallet_address: str, message: dict):
        """Send a message to all connections monitoring a specific wallet."""
        if wallet_address not in self.active_connections:
            return
        
        message_json = json.dumps(message)
        disconnected_connections = set()
        
        for websocket in self.active_connections[wallet_address]:
            try:
                await websocket.send_text(message_json)
            except Exception as e:
                logger.error(f"Error sending message to WebSocket: {e}")
                disconnected_connections.add(websocket)
        
        # Clean up disconnected connections
        for websocket in disconnected_connections:
            await self.disconnect(websocket, wallet_address)
    
    async def broadcast_deposit_update(self, wallet_address: str, deposit_data: dict):
        """Broadcast a deposit update to all connections monitoring the wallet."""
        message = {
            "type": "deposit_update",
            "wallet_address": wallet_address,
            "data": deposit_data
        }
        await self.send_to_wallet(wallet_address, message)
    
    async def broadcast_confirmation_update(self, wallet_address: str, tx_hash: str, confirmations: int, status: str):
        """Broadcast a confirmation update to all connections monitoring the wallet."""
        message = {
            "type": "confirmation_update",
            "wallet_address": wallet_address,
            "tx_hash": tx_hash,
            "confirmations": confirmations,
            "status": status
        }
        await self.send_to_wallet(wallet_address, message)
    
    def get_connection_count(self) -> int:
        """Get the total number of active connections."""
        return len(self.connection_wallets)
    
    def get_monitored_wallets(self) -> List[str]:
        """Get list of wallet addresses being monitored."""
        return list(self.active_connections.keys())
    
    def get_wallet_connection_count(self, wallet_address: str) -> int:
        """Get the number of connections monitoring a specific wallet."""
        return len(self.active_connections.get(wallet_address, set()))
