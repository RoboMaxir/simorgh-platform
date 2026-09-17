"""
SIMORGH Platform API - Billing Models

Credit-based billing system for tracking usage and subscriptions.
Ledger-based billing ensures every credit change is tracked with:
- transaction type
- amount
- reference type
- reference id
- timestamp
"""
from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, DateTime, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
import enum
from datetime import datetime, timezone

from app.models.base import Base, UUIDMixin, TimestampMixin


class TransactionType(enum.Enum):
    """Transaction type for credit changes."""
    CREDIT = "credit"  # Adding credits (purchase, grant)
    DEBIT = "debit"  # Consuming credits (usage)
    ADJUSTMENT = "adjustment"  # Manual adjustment
    REFUND = "refund"  # Refund of a previous debit


class SubscriptionTier(enum.Enum):
    """Subscription tier levels."""
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class CreditAccount(Base, UUIDMixin, TimestampMixin):
    """Credit account for a workspace."""

    __tablename__ = "credit_accounts"

    workspace_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    balance = Column(Integer, default=0, nullable=False)  # Credits in cents/smallest unit
    currency = Column(String(3), default="USD", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    workspace = relationship("Workspace", backref="credit_account")
    transactions = relationship("CreditTransaction", back_populates="account", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<CreditAccount workspace={self.workspace_id} balance={self.balance}>"

    def has_sufficient_credits(self, amount: int) -> bool:
        """Check if account has sufficient credits."""
        return self.balance >= amount

    def deduct_credits(self, amount: int) -> bool:
        """Deduct credits from account. Returns False if insufficient."""
        if not self.has_sufficient_credits(amount):
            return False
        self.balance -= amount
        return True

    def add_credits(self, amount: int) -> None:
        """Add credits to account."""
        self.balance += amount


class CreditTransaction(Base, UUIDMixin, TimestampMixin):
    """Transaction record for credit changes.
    
    Every credit change must have:
    - transaction type
    - amount
    - reference type
    - reference id
    - timestamp
    """

    __tablename__ = "credit_transactions"

    account_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("credit_accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    transaction_type = Column(SQLEnum(TransactionType), nullable=False)
    amount = Column(Integer, nullable=False)  # Positive for credits, negative for debits
    balance_after = Column(Integer, nullable=False)
    description = Column(String(500), nullable=True)
    reference_type = Column(String(50), nullable=True)  # ai_usage, subscription, manual, refund
    reference_id = Column(PG_UUID(as_uuid=True), nullable=True)
    metadata_json = Column(Text, nullable=True)  # JSON metadata

    # Relationships
    account = relationship("CreditAccount", back_populates="transactions")

    def __repr__(self) -> str:
        return f"<CreditTransaction {self.transaction_type.value} {self.amount}>"


class UsageLedger(Base, UUIDMixin, TimestampMixin):
    """Usage ledger for tracking AI service consumption.
    
    Required fields for billing integration:
    - tenant_id
    - application_id
    - workspace_id
    - request_id
    - provider
    - model
    - operation
    - input_tokens
    - output_tokens
    - estimated_cost
    - status
    """

    __tablename__ = "usage_ledgers"

    tenant_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    workspace_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    application_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("applications.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    request_id = Column(String(64), nullable=False, index=True)
    provider = Column(String(50), nullable=False)
    model = Column(String(100), nullable=False)
    operation = Column(String(50), nullable=False)  # chat, embeddings, etc.
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    estimated_cost = Column(Integer, default=0, nullable=False)  # Cost in smallest currency unit
    status = Column(String(20), nullable=False)  # success, error, pending
    error_message = Column(Text, nullable=True)
    metadata_json = Column(Text, nullable=True)  # JSON metadata

    # Relationships
    tenant = relationship("Tenant")
    workspace = relationship("Workspace")
    application = relationship("Application")

    def __repr__(self) -> str:
        return f"<UsageLedger {self.request_id} ({self.provider}/{self.model})>"


class SubscriptionPlan(Base, UUIDMixin, TimestampMixin):
    """Subscription plan definition."""

    __tablename__ = "subscription_plans"

    name = Column(String(100), nullable=False)
    slug = Column(String(50), nullable=False, unique=True)
    tier = Column(SQLEnum(SubscriptionTier), nullable=False, default=SubscriptionTier.FREE)
    price_monthly = Column(Integer, default=0, nullable=False)  # Price in cents
    credits_included = Column(Integer, default=0, nullable=False)  # Monthly credits included
    rate_limit_per_minute = Column(Integer, default=60, nullable=False)
    rate_limit_per_day = Column(Integer, default=10000, nullable=False)
    max_workspaces = Column(Integer, default=1, nullable=False)
    features = Column(Text, nullable=True)  # JSON array of features
    is_active = Column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        return f"<SubscriptionPlan {self.name}>"


class Subscription(Base, UUIDMixin, TimestampMixin):
    """Active subscription for a workspace."""

    __tablename__ = "subscriptions"

    workspace_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    plan_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("subscription_plans.id"),
        nullable=False,
    )
    status = Column(String(20), default="active", nullable=False)  # active, cancelled, past_due
    current_period_start = Column(DateTime(timezone=True), nullable=False)
    current_period_end = Column(DateTime(timezone=True), nullable=False)
    cancel_at_period_end = Column(Boolean, default=False, nullable=False)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    workspace = relationship("Workspace", backref="subscription")
    plan = relationship("SubscriptionPlan")

    def __repr__(self) -> str:
        return f"<Subscription workspace={self.workspace_id} plan={self.plan_id}>"

    @property
    def is_active(self) -> bool:
        return self.status == "active"
