from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, TYPE_CHECKING, Optional
from uuid import UUID

if TYPE_CHECKING:
    from .wallet import WalletResponse


class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


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
