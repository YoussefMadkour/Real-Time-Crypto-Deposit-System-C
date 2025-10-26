from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://postgres:password@localhost:5432/crypto_deposits"
    
    # Alchemy API
    alchemy_api_key: str
    alchemy_ws_url: str
    alchemy_http_url: str
    
    # Blockchain Configuration
    chain_id: int = 11155111  # Sepolia testnet
    confirmations_required: int = 12
    
    # Application Configuration
    secret_key: str = "dev_secret_key_change_in_production"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    api_base_url: str = "http://localhost:8000"
    
    # WebSocket Configuration
    websocket_ping_interval: int = 20
    websocket_ping_timeout: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
