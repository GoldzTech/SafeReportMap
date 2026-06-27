from __future__ import annotations

import sys
from logging.config import fileConfig
from os.path import abspath, dirname

from alembic import context
from sqlalchemy import engine_from_config, pool

# Root do repositório e pasta backend
REPO_ROOT = dirname(dirname(dirname(abspath(__file__))))
BACKEND_DIR = dirname(dirname(abspath(__file__)))

# Deixa os dois estilos de import funcionando durante a transição
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from backend.app.core.config import settings
from backend.app.db.base import Base
import backend.app.models  # noqa: F401  # registra os models no metadata

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()