from sqlalchemy import (
    Column,
    String,
    DateTime,
    Boolean,
    Integer,
    BigInteger,
    Numeric,
    ForeignKey,
    Enum,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.database import Base


class DepositStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMING = "confirming"
    COMPLETED = "completed"
    FAILED = "failed"
    ORPHANED = "orphaned"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    wallets = relationship(
        "Wallet", back_populates="user", cascade="all, delete-orphan"
    )


class BlockchainNetwork(Base):
    __tablename__ = "blockchain_networks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    chain_id = Column(Integer, nullable=False, index=True)
    rpc_url = Column(String, nullable=False)
    ws_url = Column(String, nullable=False)
    confirmations_required = Column(Integer, nullable=False, default=12)
    block_time = Column(Integer, nullable=False, default=12)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    wallets = relationship("Wallet", back_populates="blockchain_network")
    deposits = relationship("Deposit", back_populates="blockchain_network")


class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    address = Column(String, unique=True, index=True, nullable=False)
    blockchain_network_id = Column(
        UUID(as_uuid=True), ForeignKey("blockchain_networks.id"), nullable=False
    )
    label = Column(
        String, nullable=True
    )  # Optional label like "Main Wallet", "Trading Wallet"
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    user = relationship("User", back_populates="wallets")
    blockchain_network = relationship("BlockchainNetwork", back_populates="wallets")
    deposits = relationship(
        "Deposit", back_populates="wallet", cascade="all, delete-orphan"
    )


class Deposit(Base):
    __tablename__ = "deposits"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    wallet_id = Column(
        UUID(as_uuid=True), ForeignKey("wallets.id"), nullable=False, index=True
    )
    tx_hash = Column(String, unique=True, index=True, nullable=False)
    amount = Column(
        Numeric(precision=36, scale=18), nullable=False
    )  # High precision for crypto amounts
    confirmations = Column(Integer, nullable=False, default=0)
    status = Column(
        Enum(DepositStatus, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=DepositStatus.PENDING,
        index=True,
    )
    blockchain_network_id = Column(
        UUID(as_uuid=True), ForeignKey("blockchain_networks.id"), nullable=False
    )
    block_number = Column(BigInteger, nullable=True)
    block_hash = Column(String, nullable=True)  # For reorg detection
    from_address = Column(String, nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    wallet = relationship("Wallet", back_populates="deposits")
    blockchain_network = relationship("BlockchainNetwork", back_populates="deposits")
