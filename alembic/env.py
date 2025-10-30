import sys
from pathlib import Path
from sqlalchemy import engine_from_config, pool
from sqlalchemy.engine import Connection

# Додаємо корінь проєкту (де лежить папка src) до шляхів пошуку модулів
# Це потрібно, щоб Alembic міг знайти наші модулі, такі як src.car_qr_service
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from logging.config import fileConfig
from sqlalchemy.ext.asyncio import create_async_engine, async_engine_from_config
from alembic import context

# Імпортуємо наш базовий клас для моделей та самі моделі
from src.car_qr_service.database.database import Base
from src.car_qr_service.database.models import User, Car # noqa
# Імпортуємо наші налаштування, щоб взяти DB_URL
from src.car_qr_service.config import settings

# Це об'єкт Alembic Config, який надає доступ до
# значень у файлі .ini.
config = context.config

# Встановлюємо sqlalchemy.url з наших налаштувань
# Це гарантує, що Alembic і додаток дивляться на одну і ту ж БД
config.set_main_option('sqlalchemy.url', settings.SYNC_DB_URL)

# Інтерпретуємо конфігураційний файл для логування Python.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# target_metadata — це місце, де Alembic шукає моделі для автогенерації.
# Ми вказуємо йому на Base.metadata з нашого проєкту.
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode FOR SYNC.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
