import os
import sys
from logging.config import fileConfig

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy import create_engine, pool
from alembic import context

from app.core.database import Base, DATABASE_URL
import app.models.models  # Import ORM models so Base.metadata is populated

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Set Database URL dynamically from environment
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# target metadata for 'autogenerate' support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
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
    # Check if a connection was passed in configuration attributes (e.g. during unit tests)
    connectable = config.attributes.get('connection', None)

    if connectable is None:
        url = config.get_main_option("sqlalchemy.url")
        connectable = create_engine(url, poolclass=pool.NullPool)

        with connectable.connect() as connection:
            context.configure(
                connection=connection, target_metadata=target_metadata
            )

            with context.begin_transaction():
                context.run_migrations()
    else:
        context.configure(
            connection=connectable, target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
