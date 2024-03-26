import asyncio
import warnings
from pathlib import Path
from typing import AsyncIterable, Iterable

import pytest
from asyncpg import DuplicateDatabaseError  # type: ignore
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSessionTransaction, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from heavy_stack.backend.data.db_connection import (
    clear_current_db_session,
    set_current_db_session,
)
from heavy_stack.backend.data.sa_warnings_as_errors import enable_sa_warnings_as_errors
from tests.heavy_session import HeavySession

TEST_POSTGRES_HOST_URL = "postgresql+asyncpg://postgres:postgres@localhost:5555/"
TEST_POSTGRES_SQL_DB_URL = TEST_POSTGRES_HOST_URL + "postgres"
TEST_POSTGRES_HR_URL = TEST_POSTGRES_HOST_URL + "heavy_stack_test"
TEST_POSTGRES_VECTOR_URL = TEST_POSTGRES_HOST_URL + "heavy_stack_vector_test"


async def create_database(db_name: str):
    engine = create_async_engine(TEST_POSTGRES_SQL_DB_URL)
    # Obtain a raw database connection
    conn = await engine.raw_connection()
    # Cast to asyncpg connection to set transaction state
    asyncpg_conn = conn.driver_connection
    assert asyncpg_conn
    try:
        await asyncpg_conn.execute(f"CREATE DATABASE {db_name}")
    except DuplicateDatabaseError:
        pass
    except Exception as e:
        print(f"Database {db_name} could not be created: {e}")
        raise


async def create_extension(db_name: str, extension_name: str):
    engine = create_async_engine(TEST_POSTGRES_SQL_DB_URL)
    # Obtain a raw database connection
    conn = await engine.raw_connection()
    # Cast to asyncpg connection to set transaction state
    asyncpg_conn = conn.driver_connection
    assert asyncpg_conn
    try:
        await asyncpg_conn.execute(f"CREATE EXTENSION IF NOT EXISTS {extension_name}")
    except Exception as e:
        print(f"Could not create extension {extension_name} on {db_name}: {e}")
        raise


async def get_engine():
    postgres_url = TEST_POSTGRES_HR_URL
    return create_async_engine(postgres_url, echo=False)


async def recreate_tables(engine: AsyncEngine) -> None:
    from heavy_stack.backend.data import sql_models  # noqa

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)


# Trying to optimize this? Don't! Pytest asyncio creates a new
# event loop for each test, so you can't reuse the same one.
# this prevents sharing connections across tests
@pytest.fixture()
def db_session(db_session_async: HeavySession) -> Iterable[HeavySession]:
    token = set_current_db_session(db_session_async)
    yield db_session_async
    clear_current_db_session(token)


# workaround for https://github.com/pytest-dev/pytest-asyncio/issues/127
@pytest.fixture()
async def db_session_async() -> AsyncIterable[HeavySession]:
    bind = create_async_engine(TEST_POSTGRES_HR_URL)
    sm: sessionmaker = sessionmaker(  # type: ignore
        bind=bind,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    session: AsyncSession = sm()
    try:
        transaction: AsyncSessionTransaction = session.begin_nested()
        async with await transaction.start():
            yield HeavySession(session)
            await transaction.rollback()
    finally:
        await session.close()


@pytest.fixture(scope="session", autouse=True)
def make_db():
    async def _make_db():
        await create_database("heavy_stack_test")
        await create_database("heavy_stack_vector_test")
        await create_extension("heavy_stack_vector_test", "vector")
        engine = await get_engine()
        await recreate_tables(engine)

    asyncio.run(_make_db())


@pytest.fixture(scope="session", autouse=True)
def error_on_warnings():
    warnings.simplefilter("error")
    enable_sa_warnings_as_errors()
    warnings.filterwarnings("ignore", category=pytest.PytestUnraisableExceptionWarning)


@pytest.fixture()
def vector_db_session(vector_db_session_async: HeavySession) -> Iterable[HeavySession]:
    token = set_current_db_session(vector_db_session_async)
    yield vector_db_session_async
    clear_current_db_session(token)


# workaround for https://github.com/pytest-dev/pytest-asyncio/issues/127
@pytest.fixture()
async def vector_db_session_async() -> AsyncIterable[HeavySession]:
    bind = create_async_engine(TEST_POSTGRES_VECTOR_URL)
    sm: sessionmaker = sessionmaker(  # type: ignore
        bind=bind,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    session: AsyncSession = sm()
    try:
        transaction: AsyncSessionTransaction = session.begin_nested()
        async with await transaction.start():
            yield HeavySession(session)
            await transaction.rollback()
    finally:
        await session.close()
