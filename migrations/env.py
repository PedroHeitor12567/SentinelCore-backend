import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import Connection, pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from sentinelcore.core.config.settings import get_settings
from sentinelcore.infrastructure.database.base import Base
from sentinelcore.modules.authentication.infrastructure.models import refresh_token_model  # noqa: F401
from sentinelcore.modules.identity.infrastructure import models  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _get_database_url() -> str:
    override_url = config.get_main_option("sqlalchemy.url")
    if override_url:
        return override_url
    return get_settings().database_url


def run_migrations_offline() -> None:
    context.configure(
        url=_get_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def _do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = _get_database_url()

    connectable = async_engine_from_config(configuration, prefix="sqlalchemy.", poolclass=pool.NullPool)

    async with connectable.connect() as connection:
        await connection.run_sync(_do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
