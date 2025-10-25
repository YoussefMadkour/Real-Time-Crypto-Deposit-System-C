from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID
from decimal import Decimal
from app.models.user import DepositStatus

if TYPE_CHECKING:
    from .wallet import WalletResponse


class DepositBase(BaseModel):
    tx_hash: str
    amount: Decimal
    confirmations: int = 0
    status: DepositStatus = DepositStatus.PENDING
    block_number: Optional[int] = None
    block_hash: Optional[str] = None
    from_address: Optional[str] = None


class DepositCreate(DepositBase):
    wallet_id: UUID
    blockchain_network_id: UUID


class DepositUpdate(BaseModel):
    confirmations: Optional[int] = None
    status: Optional[DepositStatus] = None
    block_number: Optional[int] = None
    block_hash: Optional[str] = None


class DepositResponse(DepositBase):
    id: UUID
    wallet_id: UUID
    blockchain_network_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# class DepositWithWallet(DepositResponse):
#     wallet: "WalletResponse"

#     class Config:
#         from_attributes = True


# WebSocket event schemas
class DepositEvent(BaseModel):
    type: str  # "deposit_detected", "confirmation_update", "deposit_completed", "deposit_orphaned"
    data: DepositResponse


class ConfirmationUpdateEvent(BaseModel):
    type: str = "confirmation_update"
    tx_hash: str
    confirmations: int
    status: DepositStatus
