import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

import app.models  # ensures models are imported
from app import Base  # DeclarativeBase from app/__init__.py

# Alembic Config object, points to alembic.ini
config = context.config

# Logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata for autogenerate
target_metadata = Base.metadata


def get_url() -> str:
    """
    Return the database URL for Alembic.

    Prefer DATABASE_URL (Render), fall back to local dev DB.
    Also normalize the prefix so SQLAlchemy 2.x + psycopg works.
    """
    url = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://fwc_user:fwc_pass@localhost:5433/fwc_db",
    )

    # If Render is giving something like postgres://..., normalize it
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)

    return url


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_url()

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # Start from alembic.ini config section
    configuration = config.get_section(config.config_ini_section) or {}

    # Force sqlalchemy.url to come from our env based URL
    configuration["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
