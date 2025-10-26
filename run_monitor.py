#!/usr/bin/env python3
"""
Blockchain Monitor Service Runner

This script runs the blockchain monitoring service as a standalone process.
It monitors Ethereum Sepolia testnet for deposits to registered wallets.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent))

from app.services.blockchain_monitor import BlockchainMonitor
from app.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('blockchain_monitor.log')
    ]
)

# Reduce SQLAlchemy logging noise
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.pool').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def main():
    """Main function to run the blockchain monitor."""
    logger.info("Starting Crypto Deposit Monitor Service")
    logger.info(f"Monitoring chain ID: {settings.chain_id}")
    logger.info(f"Required confirmations: {settings.confirmations_required}")
    
    monitor = BlockchainMonitor()
    
    try:
        await monitor.start_monitoring()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
    except Exception as e:
        logger.error(f"Monitor service error: {e}")
    finally:
        await monitor.stop_monitoring()
        logger.info("Blockchain monitor service stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Service interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
