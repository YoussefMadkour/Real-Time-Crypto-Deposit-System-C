from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api import users, wallets, deposits, websocket

# Create FastAPI application
app = FastAPI(
    title="Crypto Deposit Monitor",
    description="Real-time cryptocurrency deposit monitoring system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware for WebSocket support
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


@app.get("/")
async def root():
    """Root endpoint with basic API information."""
    return {
        "message": "Crypto Deposit Monitor API",
        "version": "1.0.0",
        "docs": "/docs",
        "websocket": "/ws"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "crypto-deposit-monitor"}
