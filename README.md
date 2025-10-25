# Crypto Deposit Monitor

A real-time cryptocurrency deposit monitoring system built with FastAPI, WebSockets, PostgreSQL, and Alchemy API.

## Features

- Real-time blockchain transaction monitoring
- WebSocket-based live status updates
- Multi-wallet support per user
- Blockchain reorganization detection
- Configurable confirmation requirements per network
- Docker containerization for easy deployment

## Architecture

- **FastAPI REST API** - User management and deposit queries
- **WebSocket Server** - Real-time deposit status updates
- **Blockchain Monitor Service** - Background worker monitoring Ethereum Sepolia
- **PostgreSQL Database** - Persistent storage with SQLAlchemy ORM
- **Alchemy Integration** - Blockchain connectivity via WebSocket and HTTP

## Prerequisites

- Python 3.11+
- Docker and Docker Compose
- Alchemy API key (get one at [alchemy.com](https://alchemy.com))

## Quick Start with Docker

1. Clone the repository and navigate to the project directory
2. Copy `.env.example` to `.env` and fill in your Alchemy API key:
   ```bash
   cp .env.example .env
   # Edit .env and add your ALCHEMY_API_KEY
   ```
3. Start the services:
   ```bash
   docker-compose up --build
   ```
4. The API will be available at `http://localhost:8000`
5. API documentation at `http://localhost:8000/docs`

## Local Development Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up PostgreSQL database (using Docker):
   ```bash
   docker run --name postgres-crypto -e POSTGRES_DB=crypto_deposits -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres:17
   ```

4. Copy environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your database URL and Alchemy API key
   ```

5. Run database migrations:
   ```bash
   alembic upgrade head
   ```

6. Start the API server:
   ```bash
   uvicorn app.main:app --reload
   ```

7. Start the blockchain monitor (in another terminal):
   ```bash
   python run_monitor.py
   ```

## API Endpoints

### Users
- `POST /users/` - Create a new user
- `GET /users/{user_id}` - Get user by ID
- `GET /users/by-email/{email}` - Get user by email

### Wallets
- `POST /wallets/` - Add a wallet to a user
- `GET /wallets/user/{user_id}` - Get all wallets for a user
- `GET /wallets/{wallet_id}` - Get wallet by ID

### Deposits
- `GET /deposits/wallet/{wallet_id}` - Get deposits for a wallet
- `GET /deposits/{deposit_id}` - Get deposit by ID
- `GET /deposits/tx/{tx_hash}` - Get deposit by transaction hash

### WebSocket
- `WS /ws?wallet_address=0x...` - Connect to real-time updates for a wallet

## WebSocket Events

The WebSocket connection sends real-time updates in JSON format:

```json
{
  "type": "deposit_detected",
  "data": {
    "tx_hash": "0x...",
    "amount": "1.5",
    "confirmations": 0,
    "status": "pending"
  }
}
```

Event types:
- `deposit_detected` - New deposit found
- `confirmation_update` - Confirmation count increased
- `deposit_completed` - Deposit fully confirmed
- `deposit_orphaned` - Transaction removed due to blockchain reorg

## Testing the System

1. Create a user and add a wallet address
2. Get some Sepolia test ETH from a faucet (e.g., [sepoliafaucet.com](https://sepoliafaucet.com))
3. Send ETH to your monitored wallet address
4. Connect to the WebSocket endpoint to see real-time updates
5. Check the API endpoints to see deposit history

## Environment Variables

See `.env.example` for all required environment variables.

## Database Schema

The system uses PostgreSQL with the following main tables:
- `users` - User accounts
- `wallets` - Wallet addresses (multiple per user)
- `deposits` - Transaction records with status tracking
- `blockchain_networks` - Supported blockchain configurations

## Security Notes

- Authentication is simplified for this technical demo
- In production, implement JWT authentication
- Wallet addresses are validated for proper format
- All amounts use precise decimal arithmetic

## Architecture Decisions

### Blockchain Monitoring
- Uses Alchemy WebSocket API for real-time block notifications
- Implements `eth_newBlockHeaders` subscription for new blocks
- Uses `eth_getTransactionReceipt` for transaction verification
- Tracks block hashes to detect blockchain reorganizations

### Real-Time Updates
- WebSocket connections authenticated by wallet address
- Connection manager handles multiple concurrent users
- Graceful handling of connection drops and reconnections

### Database Design
- UUIDs for all primary keys (better for distributed systems)
- Separate wallets table for multi-wallet support
- Configurable confirmation requirements per network
- Comprehensive indexing for fast lookups

## Contributing

This is a technical assessment project. The codebase demonstrates:
- Clean, modular architecture
- Real-time system design
- Blockchain integration best practices
- Production-ready error handling
- Comprehensive documentation
