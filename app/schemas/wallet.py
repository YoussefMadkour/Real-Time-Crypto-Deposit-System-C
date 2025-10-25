from pydantic import BaseModel, validator
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from .deposit import DepositResponse


class WalletBase(BaseModel):
    address: str
    label: Optional[str] = None
    is_active: bool = True

    @validator('address')
    def validate_address(cls, v):
        """Basic Ethereum address validation."""
        if not v.startswith('0x'):
            raise ValueError('Address must start with 0x')
        if len(v) != 42:
            raise ValueError('Address must be 42 characters long')
        # Convert to lowercase for consistency
        return v.lower()


class WalletCreate(WalletBase):
    user_id: UUID
    blockchain_network_id: UUID


class WalletResponse(WalletBase):
    id: UUID
    user_id: UUID
    blockchain_network_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# class WalletWithDeposits(WalletResponse):
#     deposits: List["DepositResponse"] = []

#     class Config:
#         from_attributes = True
