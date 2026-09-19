"""
SIMORGH Platform API - User Model

Represents a human user in the platform.
Users belong to workspaces and have roles.
"""
from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.models.base import Base, UUIDMixin, TimestampMixin


class User(Base, UUIDMixin, TimestampMixin):
    """User model for human users."""

    __tablename__ = "users"

    workspace_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    email = Column(String(255), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    password_hash = Column(String(255), nullable=False)  # Argon2 hash
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    workspace = relationship("Workspace", backref="users")
    user_roles = relationship(
        "UserRole",
        back_populates="user",
        foreign_keys="UserRole.user_id",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User {self.email}>"

    @property
    def is_authenticated(self) -> bool:
        return self.is_active


class Role(Base, UUIDMixin, TimestampMixin):
    """Role model for RBAC."""

    __tablename__ = "roles"

    workspace_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String(50), nullable=False)
    slug = Column(String(50), nullable=False, unique=True)
    description = Column(String(500), nullable=True)
    is_system = Column(Boolean, default=False, nullable=False)  # System roles cannot be deleted

    # Relationships
    workspace = relationship("Workspace", backref="roles")
    permissions = relationship("RolePermission", back_populates="role", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Role {self.name}>"


class Permission(Base, UUIDMixin, TimestampMixin):
    """Permission model for fine-grained access control."""

    __tablename__ = "permissions"

    name = Column(String(100), nullable=False, unique=True)
    description = Column(String(500), nullable=True)
    resource = Column(String(50), nullable=False)  # e.g., "application", "api_key"
    action = Column(String(20), nullable=False)  # e.g., "create", "read", "update", "delete"

    def __repr__(self) -> str:
        return f"<Permission {self.name}>"


class UserRole(Base, UUIDMixin, TimestampMixin):
    """Association table for users and roles."""

    __tablename__ = "user_roles"

    user_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    granted_by = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )
    granted_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    user = relationship("User", back_populates="user_roles", foreign_keys=[user_id])
    role = relationship("Role", back_populates="permissions")
    granter = relationship("User", foreign_keys=[granted_by])

    def __repr__(self) -> str:
        return f"<UserRole user={self.user_id} role={self.role_id}>"


class RolePermission(Base, UUIDMixin, TimestampMixin):
    """Association table for roles and permissions."""

    __tablename__ = "role_permissions"

    role_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    permission_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("permissions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Relationships
    role = relationship("Role", back_populates="permissions", foreign_keys=[role_id])
    permission = relationship("Permission")

    def __repr__(self) -> str:
        return f"<RolePermission role={self.role_id} permission={self.permission_id}>"
