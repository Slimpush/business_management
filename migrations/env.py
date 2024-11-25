import asyncio
from logging.config import fileConfig
import os
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context
from src.models.models import Base
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Читаем конфигурацию из alembic.ini
config = context.config

# Сборка строки подключения из переменных окружения
DATABASE_URL = (
    f"postgresql+asyncpg://{os.environ['DB_USER']}:{os.environ['DB_PASS']}@"
    f"{os.environ['DB_HOST']}:{os.environ['DB_PORT']}/{os.environ['DB_NAME']}"
)

# Указываем строку подключения в конфиг Alembic
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Настройка логирования (если используется файл конфигурации логов)
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Метаинформация моделей
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Запуск миграций в оффлайн-режиме."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    connectable = create_async_engine(
        DATABASE_URL,
    )

    try:
        async with connectable.connect() as connection:
            await connection.run_sync(do_run_migrations)
    finally:
        await connectable.dispose()


def do_run_migrations(connection):
    """Синхронный запуск миграций."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        render_as_batch=True,  # Используйте, если нужна поддержка batch mode
    )

    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
