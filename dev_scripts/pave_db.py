import asyncio
import os

from asyncpg import DuplicateDatabaseError  # type: ignore
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlmodel import SQLModel

from heavy_stack.backend.data import sql_models  # noqa

sql_db_url = os.environ["SETME_ENV_PREFIX_SQL_DB_URL"]
vector_db_url = os.environ["SETME_ENV_PREFIX_VECTOR_DB_URL"]

if "localhost" not in sql_db_url:
    raise Exception("Not dev URLs!!!")
if "localhost" not in vector_db_url:
    raise Exception("Not dev URLS!!!")


async def create_database(db_url: str, db_name: str) -> None:
    engine = create_async_engine(db_url)
    # Obtain a raw database connection
    conn = await engine.raw_connection()
    try:
        # Cast to asyncpg connection to set transaction state
        asyncpg_conn = conn.connection._connection  # type: ignore
        try:
            await asyncpg_conn.execute(f"CREATE DATABASE {db_name}")
        except DuplicateDatabaseError:
            pass
        except Exception as e:
            print(f"Database {db_name} could not be created: {e}")
            raise
    finally:
        conn.close()


async def get_engine() -> AsyncEngine:
    return create_async_engine(sql_db_url, echo=True)


async def pave_db() -> None:
    await create_database(sql_db_url.rsplit("/", 1)[0], "heavy_stack")
    await create_database(vector_db_url.rsplit("/", 1)[0], "heavy_stack_vector")
    engine = await get_engine()
    await recreate_tables(engine)


async def recreate_tables(engine: AsyncEngine) -> None:
    from heavy_stack.backend.data import sql_models  # noqa

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(pave_db())
