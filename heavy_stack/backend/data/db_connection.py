from contextvars import ContextVar, Token

from sqlalchemy import Engine, create_engine
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from heavy_stack.config import get_config

config = get_config()

_current_db_session: ContextVar[AsyncSession] = ContextVar("db_session")


def set_current_db_session(db_session: AsyncSession) -> Token[AsyncSession]:
    return _current_db_session.set(db_session)


def get_current_db_session() -> AsyncSession:
    return _current_db_session.get()


# prefer close_current_db_session
# this exists because of pytest-asyncio limitation
def clear_current_db_session(token: Token[AsyncSession]) -> None:
    _current_db_session.reset(token)


async def close_current_db_session(token: Token[AsyncSession]) -> None:
    session = get_current_db_session()
    await session.rollback()
    await session.close()
    clear_current_db_session(token)


sql_db_url = config.SQL_DB_URL
vector_db_url = config.VECTOR_DB_URL


def create_db_engine() -> AsyncEngine:
    # pool pre ping - executes SELECT 1 to check the connection. Without this, a connection may error on first use.
    #                 This incurs a small cost with checking the connection, so long term an optimistic approach may be better.
    # pool use lifo - reuse recent connections, allowing older ones to die if they aren't utilized.
    return create_async_engine(sql_db_url, pool_use_lifo=True, pool_pre_ping=True)


def create_vector_db_engine() -> AsyncEngine:
    bind = create_async_engine(vector_db_url, pool_pre_ping=True)
    return bind


def create_sync_vector_db_engine() -> Engine:
    sync_url = vector_db_url.replace("postgresql+asyncpg", "postgresql+psycopg2").replace("?ssl=verify-full", "?")
    bind = create_engine(sync_url, pool_pre_ping=True)
    return bind
