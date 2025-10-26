from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID


class BlockchainNetworkBase(BaseModel):
    name: str
    chain_id: int
    rpc_url: str
    ws_url: str
    confirmations_required: int = 12
    is_active: bool = True


class BlockchainNetworkCreate(BlockchainNetworkBase):
    pass


class BlockchainNetworkResponse(BlockchainNetworkBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class BlockchainNetworkUpdate(BaseModel):
    name: Optional[str] = None
    chain_id: Optional[int] = None
    rpc_url: Optional[str] = None
    ws_url: Optional[str] = None
    confirmations_required: Optional[int] = None
    is_active: Optional[bool] = None
