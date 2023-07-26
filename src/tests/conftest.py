import asyncio
from typing import AsyncGenerator

import asyncpg
import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from db import get_session
from db.models import ShortUrl
from src.main import app

from .mocks import TEST_DB_NAME, database_dsn

base_url = 'http://localhost:8080'


@pytest.fixture(scope='session')
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='function')
async def client() -> AsyncGenerator:
    async with AsyncClient(
        app=app, follow_redirects=False, base_url=base_url
    ) as client:
        yield client


async def create_test_db() -> None:
    user, password, database = 'postgres', 'postgres', TEST_DB_NAME
    try:
        await asyncpg.connect(database=database, user=user, password=password)
    except asyncpg.InvalidCatalogNameError:
        conn = await asyncpg.connect(
            database='postgres', user=user, password=password
        )
        sql_command = text(
            f'CREATE DATABASE "{database}" OWNER "{user}" ENCODING "utf8"'
        )
        await conn.execute(sql_command)
        await conn.close()
        await asyncpg.connect(database=database, user=user, password=password)


@pytest.fixture(scope='module')
async def async_session() -> AsyncGenerator[AsyncSession, None]:
    await create_test_db()
    engine = create_async_engine(database_dsn, echo=False, future=True)
    session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with engine.begin() as conn:
        await conn.run_sync(ShortUrl.metadata.drop_all)
        await conn.run_sync(ShortUrl.metadata.create_all)
    async with session() as session:

        def get_session_override():
            return session

        app.dependency_overrides[get_session] = get_session_override
        yield session
    await engine.dispose()
