from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.config import settings
from app.api import users, wallets, deposits, websocket, blockchain_networks
import os

# Create FastAPI application
app = FastAPI(
    title="Crypto Deposit Monitor",
    description="Real-time cryptocurrency deposit monitoring system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware for WebSocket support
# TODO: Restrict origins in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(wallets.router, prefix="/wallets", tags=["wallets"])
app.include_router(deposits.router, prefix="/deposits", tags=["deposits"])
app.include_router(websocket.router, prefix="/ws", tags=["websocket"])
app.include_router(
    blockchain_networks.router,
    prefix="/blockchain-networks",
    tags=["blockchain-networks"],
)


# Mount static files
static_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")


@app.get("/")
async def root():
    """Serve the main HTML page."""
    html_path = os.path.join(static_path, "index.html")
    if os.path.exists(html_path):
        return FileResponse(html_path)
    return {
        "message": "Crypto Deposit Monitor API",
        "version": "1.0.0",
        "docs": "/docs",
        "websocket": "/ws",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "crypto-deposit-monitor"}


@app.post("/api/internal/notify-deposit")
async def notify_deposit(request: dict):
    """
    Internal endpoint for blockchain monitor to notify about new deposits.
    Monitor service (separate process) uses this to communicate with the API.
    """
    from app.services.websocket_manager import get_websocket_manager
    from app.utils import normalize_address
    
    wallet_address = normalize_address(request.get("wallet_address", ""))
    deposit_data = request.get("deposit_data", {})
    
    websocket_manager = get_websocket_manager()
    
    # Broadcast to all connected clients for this wallet
    await websocket_manager.broadcast_deposit_update(wallet_address, deposit_data)
    
    return {"status": "notified"}


@app.post("/api/internal/notify-confirmation")
async def notify_confirmation(request: dict):
    """
    Internal endpoint for blockchain monitor to notify about confirmation updates.
    """
    from app.services.websocket_manager import get_websocket_manager
    from app.utils import normalize_address
    
    wallet_address = normalize_address(request.get("wallet_address", ""))
    tx_hash = request.get("tx_hash", "")
    confirmations = request.get("confirmations", 0)
    status = request.get("status", "")
    
    websocket_manager = get_websocket_manager()
    
    # Broadcast to all connected clients for this wallet
    await websocket_manager.broadcast_confirmation_update(
        wallet_address, tx_hash, confirmations, status
    )
    
    return {"status": "notified"}
