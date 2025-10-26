import asyncio
import json
import logging
import ssl
from typing import Dict, List, Optional
from decimal import Decimal
from web3 import Web3
from web3.middleware import geth_poa_middleware
import websockets

from app.config import settings
from app.database import AsyncSessionLocal
from app.models.user import Deposit, Wallet, BlockchainNetwork, DepositStatus
from app.services.deposit_processor import DepositProcessor
from app.services.websocket_manager import get_websocket_manager
from app.schemas.deposit import DepositCreate
from app.utils import normalize_address, normalize_transaction_hash
from sqlalchemy import select

logger = logging.getLogger(__name__)


class BlockchainMonitor:
    """Monitors blockchain for new transactions and confirmations."""

    def __init__(self):
        self.w3_http = None
        self.ws_connection = None
        self.websocket_manager = get_websocket_manager()
        self.running = False
        self.monitored_wallets: Dict[str, Wallet] = {}

    async def initialize(self):
        """Initialize Web3 connections."""
        try:
            # Initialize HTTP Web3 connection
            self.w3_http = Web3(Web3.HTTPProvider(settings.alchemy_http_url))

            # Add PoA middleware for testnets
            self.w3_http.middleware_onion.inject(geth_poa_middleware, layer=0)

            # Verify connection
            if not self.w3_http.is_connected():
                raise Exception("Failed to connect to Ethereum node via HTTP")

            logger.info("Initialized HTTP Web3 connection")

            # Initialize WebSocket connection
            await self._initialize_websocket()

        except Exception as e:
            logger.error(f"Failed to initialize blockchain monitor: {e}")
            raise

    async def _initialize_websocket(self):
        """Initialize WebSocket connection to Alchemy."""
        try:
            # Create SSL context that doesn't verify certificates (for development)
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

            # Create WebSocket connection with SSL context
            self.ws_connection = await websockets.connect(
                settings.alchemy_ws_url, ssl=ssl_context
            )

            # Subscribe to new block headers
            subscribe_message = {
                "id": 1,
                "method": "eth_subscribe",
                "params": ["newHeads"],
            }

            await self.ws_connection.send(json.dumps(subscribe_message))
            response = await self.ws_connection.recv()
            response_data = json.loads(response)

            if "error" in response_data:
                raise Exception(
                    f"WebSocket subscription failed: {response_data['error']}"
                )

            logger.info("Initialized WebSocket connection and subscribed to new blocks")

        except Exception as e:
            logger.error(f"Failed to initialize WebSocket: {e}")
            raise

    async def start_monitoring(self):
        """Start the blockchain monitoring service."""
        logger.info("Starting blockchain monitor...")

        try:
            await self.initialize()
            await self.load_monitored_wallets()

            self.running = True

            # Start monitoring tasks
            tasks = [
                asyncio.create_task(self._monitor_new_blocks()),
                asyncio.create_task(self._update_confirmations()),
                asyncio.create_task(self._check_reorgs()),
            ]

            await asyncio.gather(*tasks)

        except Exception as e:
            logger.error(f"Blockchain monitor error: {e}")
        finally:
            await self.stop_monitoring()

    async def stop_monitoring(self):
        """Stop the blockchain monitoring service."""
        logger.info("Stopping blockchain monitor...")
        self.running = False

        if self.ws_connection:
            await self.ws_connection.close()

    async def load_monitored_wallets(self):
        """Load all wallets that should be monitored."""
        async with AsyncSessionLocal() as db:
            processor = DepositProcessor(db)
            wallets = await processor.get_monitored_wallets()

            self.monitored_wallets = {
                wallet.address.lower(): wallet for wallet in wallets
            }

    async def _monitor_new_blocks(self):
        """Monitor for new blocks and process transactions."""
        while self.running:
            try:
                if not self.ws_connection:
                    await self._initialize_websocket()

                # Wait for new block notification
                message = await self.ws_connection.recv()
                data = json.loads(message)

                if data.get("method") == "eth_subscription":
                    await self._process_new_block(data["params"]["result"])

            except websockets.exceptions.ConnectionClosed:
                logger.warning("WebSocket connection closed, reconnecting...")
                await asyncio.sleep(5)
                await self._initialize_websocket()
            except Exception as e:
                logger.error(f"Error in block monitoring: {e}")
                await asyncio.sleep(5)

    async def _process_new_block(self, block_data: dict):
        """Process a new block and check for relevant transactions."""
        try:
            block_number = int(block_data["number"], 16)
            block_hash = block_data["hash"]

            # Get block details with transactions
            block = self.w3_http.eth.get_block(block_number, full_transactions=True)

            # Process each transaction
            for tx in block.transactions:
                await self._process_transaction(tx, block_number, block_hash)

        except Exception as e:
            logger.error(f"Error processing block: {e}")

    async def _process_transaction(self, tx, block_number: int, block_hash: str):
        """Process a single transaction."""
        try:
            # Check if transaction is to a monitored wallet
            to_address = tx.get("to")
            if not to_address:
                return

            normalized_to = normalize_address(to_address)

            if normalized_to not in self.monitored_wallets:
                return

            wallet = self.monitored_wallets[normalized_to]

            # Get transaction receipt for status
            tx_hash = (
                tx["hash"].hex()
                if isinstance(tx.get("hash"), bytes)
                else tx.get("hash")
            )
            try:
                receipt = self.w3_http.eth.get_transaction_receipt(tx_hash)
                if receipt.status == 0:  # Failed transaction
                    return
            except Exception:
                # Transaction might not be mined yet
                pass

            # Calculate amount in ETH
            amount_wei = tx.get("value", 0)
            amount_eth = Decimal(amount_wei) / Decimal(10**18)

            # Create deposit record
            async with AsyncSessionLocal() as db:
                processor = DepositProcessor(db)
                
                # Check if deposit already exists
                existing_deposit = await processor.get_deposit_by_tx_hash(normalize_transaction_hash(tx_hash))
                if existing_deposit:
                    return

                deposit_data = DepositCreate(
                    wallet_id=wallet.id,
                    tx_hash=tx_hash,
                    amount=amount_eth,
                    confirmations=0,
                    status=DepositStatus.PENDING,
                    blockchain_network_id=wallet.blockchain_network_id,
                    block_number=block_number,
                    block_hash=block_hash,
                    from_address=normalize_address(tx.get("from", "")),
                )

                deposit = await processor.create_deposit(deposit_data)

                if deposit:
                    # Notify API (monitor runs in separate process)
                    try:
                        import httpx
                        async with httpx.AsyncClient() as client:
                            await client.post(
                                f"{settings.api_base_url}/api/internal/notify-deposit",
                                json={
                                    "wallet_address": normalized_to,
                                    "deposit_data": {
                                        "id": str(deposit.id),
                                        "tx_hash": deposit.tx_hash,
                                        "amount": str(deposit.amount),
                                        "confirmations": deposit.confirmations,
                                        "status": deposit.status.value,
                                        "block_number": deposit.block_number,
                                        "from_address": deposit.from_address,
                                    }
                                },
                                timeout=2.0
                            )
                    except Exception as e:
                        logger.error(f"Failed to notify API: {e}")

        except Exception as e:
            logger.error(f"Error processing transaction: {e}")

    async def _update_confirmations(self):
        """Periodically update confirmation counts for pending deposits."""
        while self.running:
            try:
                await asyncio.sleep(15)  # Update every 15 seconds

                async with AsyncSessionLocal() as db:
                    processor = DepositProcessor(db)

                    # Get pending deposits
                    result = await db.execute(
                        select(Deposit).where(
                            Deposit.status.in_(
                                [DepositStatus.PENDING, DepositStatus.CONFIRMING]
                            )
                        )
                    )
                    deposits = result.scalars().all()

                    current_block = self.w3_http.eth.block_number

                    # Get wallet info first (outside async loop to avoid lazy loading issues)
                    wallet_info = {}
                    for deposit in deposits:
                        if deposit.wallet_id not in wallet_info:
                            wallet = await processor.get_wallet_by_id(deposit.wallet_id)
                            if wallet:
                                wallet_info[deposit.wallet_id] = normalize_address(wallet.address)

                    for deposit in deposits:
                        if deposit.block_number:
                            confirmations = current_block - deposit.block_number

                            if confirmations != deposit.confirmations:
                                # Update confirmations
                                updated_deposit = (
                                    await processor.update_deposit_confirmations(
                                        deposit.tx_hash,
                                        confirmations,
                                        deposit.block_hash,
                                    )
                                )

                                if updated_deposit:
                                    # Notify API about confirmation update
                                    try:
                                        wallet_addr = wallet_info.get(deposit.wallet_id, "")
                                        # requests works better here than httpx
                                        import requests
                                        requests.post(
                                            f"{settings.api_base_url}/api/internal/notify-confirmation",
                                            json={
                                                "wallet_address": wallet_addr,
                                                "tx_hash": deposit.tx_hash,
                                                "confirmations": confirmations,
                                                "status": updated_deposit.status.value,
                                            },
                                            timeout=2.0
                                        )
                                    except Exception as e:
                                        logger.error(f"Failed to notify API: {e}")

            except Exception as e:
                logger.error(f"Error updating confirmations: {e}")

    async def _check_reorgs(self):
        """Check for blockchain reorganizations."""
        while self.running:
            try:
                await asyncio.sleep(60)  # Check every minute

                async with AsyncSessionLocal() as db:
                    processor = DepositProcessor(db)

                    # Get recent deposits with block hashes
                    result = await db.execute(
                        select(Deposit)
                        .where(
                            Deposit.block_hash.isnot(None),
                            Deposit.status.in_(
                                [
                                    DepositStatus.PENDING,
                                    DepositStatus.CONFIRMING,
                                    DepositStatus.COMPLETED,
                                ]
                            ),
                        )
                        .limit(100)
                    )
                    deposits = result.scalars().all()

                    for deposit in deposits:
                        if deposit.block_number and deposit.block_hash:
                            try:
                                # Check if block still exists with same hash
                                current_block = self.w3_http.eth.get_block(
                                    deposit.block_number
                                )

                                if current_block.hash.hex() != deposit.block_hash:
                                    # Block hash changed - reorg detected
                                    logger.warning(
                                        f"Reorg detected for deposit {deposit.tx_hash}"
                                    )

                                    orphaned_deposit = (
                                        await processor.mark_deposit_orphaned(
                                            deposit.tx_hash
                                        )
                                    )

                                    if orphaned_deposit:
                                        # Send WebSocket notification
                                        # Use normalized address to match the key in active_connections
                                        await self.websocket_manager.broadcast_deposit_update(
                                            normalize_address(deposit.wallet.address),
                                            {
                                                "id": str(deposit.id),
                                                "tx_hash": deposit.tx_hash,
                                                "status": DepositStatus.ORPHANED.value,
                                                "message": "Transaction orphaned due to blockchain reorganization",
                                            },
                                        )

                            except Exception as e:
                                logger.error(
                                    f"Error checking reorg for deposit {deposit.tx_hash}: {e}"
                                )

            except Exception as e:
                logger.error(f"Error in reorg detection: {e}")
