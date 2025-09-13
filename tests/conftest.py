import asyncio
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.car_qr_service.database.database import Base, get_db_session
from src.car_qr_service.main import app

# --- Налаштування тестової бази даних ---
TEST_DB_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(TEST_DB_URL, echo=True)
TestingSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


# --- Фікстури Pytest ---
@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Створює екземпляр циклу подій для всієї тестової сесії."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ЗМІНА: scope="session" -> scope="function"
@pytest.fixture(scope="function")
async def db_session() -> AsyncSession:
    """
    Створює нову сесію бази даних для кожного тесту.
    Створює таблиці перед тестом і видаляє їх після.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session = TestingSessionLocal()
    yield session
    await session.close()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
def client(db_session: AsyncSession) -> Generator:
    """
    Створює тестовий клієнт, який використовує тестову сесію бази даних.
    """

    def override_get_db_session() -> Generator:
        yield db_session

    app.dependency_overrides[get_db_session] = override_get_db_session
    yield TestClient(app)

