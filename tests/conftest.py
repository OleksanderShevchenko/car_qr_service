import asyncio
from asyncio import get_event_loop_policy, AbstractEventLoop
from typing import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker

from src.car_qr_service.database.database import Base, get_db_session
from src.car_qr_service.main import app

# Use sqlite database in memory for testing (creating each time new one)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

db_engine: AsyncEngine = create_async_engine(TEST_DATABASE_URL, echo=True)
db_async_session_maker = sessionmaker(bind=db_engine, class_=AsyncSession, expire_on_commit=False)


# this function will call before each test
@pytest.fixture(scope="session", autouse=True)
async def init_db():
    async with db_engine.begin() as db_conn:
        # create all tables basing on our models
        await db_conn.run_sync(Base.metadata.create_all)
    yield
    async with db_engine.begin() as db_conn:
        # delete all tables after using in tests
        await db_conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with db_async_session_maker() as session:
        yield session


@pytest.fixture(scope="session")
def event_loop() -> Generator[AbstractEventLoop, None, None]:
    """
    Create event loop instance for all tests
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def client(db_session: AsyncSession) -> Generator[TestClient, None, None]:
    """
    Create HTTP client for sending requests to our API
    """

    # this function is substituting our dependency get_db_session on session of test database
    def override_get_db_session() -> Generator[AsyncSession, None, None]:
        yield db_session

    # apply override
    app.dependency_overrides[get_db_session] = override_get_db_session

    with TestClient(app) as tc:
        yield tc
