from typing import Generator, AsyncGenerator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.car_qr_service.database.database import Base, get_db_session
from src.car_qr_service.main import app

# 1. Setup test database as local file in the root folder of the project
TEST_DB_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(TEST_DB_URL, echo=True)
TestingSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, bind=engine, expire_on_commit=False, class_=AsyncSession
)

# --- 2. Create and delete tables in test database ---
# This fixture runs once at start of the test session to create tables in database
# And remove them at the end of the session to work always with clear db without artefacts from previous session
@pytest.fixture(scope="session", autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

# --- 3. Database session for each individual test ---
# This fixture creates new database session for each test.
# After ending the test all changes in the database are been rolled back.
# This should guarantee that tests has no influence on each other.
@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    connection = await engine.connect()
    transaction = await connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    await session.close()
    await transaction.rollback()
    await connection.close()


# --- 4. Test Client  ---
# This fixture creates TestClient and force it to use the same database session,
# that is using by the test itself.
@pytest.fixture(scope="function")
def client(db_session: AsyncSession) -> Generator[TestClient, None, None]:
    """
    Creates TestClient, which uses same session that the test is using.
    """

    # Create a replacement function with the correct `async` signature
    async def override_get_db_session() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    # We apply dependency substitution in our application
    app.dependency_overrides[get_db_session] = override_get_db_session

    # We create and submit the client for testing
    with TestClient(app) as c:
        yield c

    # After the test is complete, we remove the "substitution" so that the tests do not affect each other
    app.dependency_overrides.clear()