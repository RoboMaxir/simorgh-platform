"""SIMORGH Platform Alembic Environment."""
import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

from app.models.base import Base
from app.config import get_settings

# Import all models to ensure they are registered with Base
from app.models import (  # noqa: F401
    Tenant,
    Workspace,
    User,
    Role,
    Permission,
    UserRole,
    RolePermission,
    Application,
    ApplicationInstallation,
    Credential,
    CreditAccount,
    CreditTransaction,
    UsageLedger,
    SubscriptionPlan,
    Subscription,
    AIUsage,
    AuditEvent,
    KnowledgeSpace,
    KnowledgeDocument,
    KnowledgeChunk,
    KnowledgeEmbedding,
    KnowledgeFile,
)

# this is the Alembic Config object
config = context.config

# Override sqlalchemy.url with settings from environment
settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.database_url)

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Model's MetaData object for 'autogenerate' support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async def run(connection: Connection) -> None:
        await connection.run_sync(context.run_migrations)

    async def main() -> None:
        async with connectable.connect() as connection:
            await connection.run_sync(run)
        await connectable.dispose()

    asyncio.run(main())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
