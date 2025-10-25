# Import all schemas to enable forward references
from .user import UserBase, UserCreate, UserResponse, UserWithWallets
from .wallet import WalletBase, WalletCreate, WalletResponse
from .deposit import DepositBase, DepositCreate, DepositUpdate, DepositResponse, DepositEvent, ConfirmationUpdateEvent

# Update forward references
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .wallet import WalletResponse
    from .deposit import DepositResponse

__all__ = [
    "UserBase", "UserCreate", "UserResponse", "UserWithWallets",
    "WalletBase", "WalletCreate", "WalletResponse", 
    "DepositBase", "DepositCreate", "DepositUpdate", "DepositResponse",
    "DepositEvent", "ConfirmationUpdateEvent"
]
