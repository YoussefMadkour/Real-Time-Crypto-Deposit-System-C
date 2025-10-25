from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from .wallet import WalletResponse


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserWithWallets(UserResponse):
    wallets: List["WalletResponse"] = []

    class Config:
        from_attributes = True


# Import WalletResponse after the class definitions to avoid circular imports
from .wallet import WalletResponse
UserWithWallets.model_rebuild()
