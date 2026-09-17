"""
SIMORGH Platform API - Billing Models

Credit-based billing system for tracking usage and subscriptions.
"""
from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, DateTime, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
import enum
from datetime import datetime, timezone

from app.models.base import Base, UUIDMixin, TimestampMixin


class SubscriptionTier(enum.Enum):
    """Subscription tier levels."""
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class CreditAccount(Base, UUIDMixin, TimestampMixin):
    """Credit account for a workspace or tenant."""

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
    """Transaction record for credit changes."""

    __tablename__ = "credit_transactions"

    account_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("credit_accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    transaction_type = Column(String(20), nullable=False)  # credit, debit, adjustment
    amount = Column(Integer, nullable=False)  # Can be negative for debits
    balance_after = Column(Integer, nullable=False)
    description = Column(String(500), nullable=True)
    reference_type = Column(String(50), nullable=True)  # ai_usage, subscription, manual
    reference_id = Column(PG_UUID(as_uuid=True), nullable=True)
    metadata_json = Column(Text, nullable=True)

    # Relationships
    account = relationship("CreditAccount", back_populates="transactions")

    def __repr__(self) -> str:
        return f"<CreditTransaction {self.transaction_type} {self.amount}>"


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


class UsageQuota(Base, UUIDMixin, TimestampMixin):
    """Usage quota tracking for rate limiting."""

    __tablename__ = "usage_quotas"

    workspace_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    requests_made = Column(Integer, default=0, nullable=False)
    tokens_used = Column(Integer, default=0, nullable=False)
    api_calls = Column(Integer, default=0, nullable=False)

    # Relationships
    workspace = relationship("Workspace")

    def __repr__(self) -> str:
        return f"<UsageQuota workspace={self.workspace_id} requests={self.requests_made}>"
