import argparse
import asyncio
import os
import subprocess
import time
from contextlib import contextmanager

from asyncpg import DuplicateDatabaseError
from sqlalchemy.ext.asyncio import create_async_engine

pg_migration_staging_url = "postgresql+asyncpg://postgres:postgres@localhost:5432/heavy_stack_migrations"
cockroach_url = "cockroachdb+asyncpg://heavy:@localhost:26257/heavy_stack"

prev_db_url = os.environ["SETME_ENV_PREFIX_SQL_DB_URL"]
os.environ[
    "DISABLE_SA_WARNINGS_AS_ERRORS"  # enum types show up as user-defined, which can't be parsed
] = "1"

if os.environ.get("SETME_ENV_PREFIX_ENVIRONMENT") == "PRODUCTION":
    raise Exception("DO NOT RUN WITH PRODUCTION ON")


async def create_database(db_name: str):
    engine = create_async_engine("postgresql+asyncpg://postgres:postgres@localhost:5432/postgres")
    # Obtain a raw database connection
    conn = await engine.raw_connection()
    try:
        # Cast to asyncpg connection to set transaction state
        asyncpg_conn = conn.connection._connection  # type: ignore
        try:
            await asyncpg_conn.execute(f"CREATE DATABASE {db_name}")
        except DuplicateDatabaseError:
            await asyncpg_conn.execute(f"DROP DATABASE {db_name}")
            await asyncpg_conn.execute(f"CREATE DATABASE {db_name}")
        except Exception as e:
            print(f"Database {db_name} could not be created: {e}")
            raise
    finally:
        conn.close()


async def create_db() -> None:
    # note: cockroach loses DB when it goes down and comes back up with empty DB
    await create_database("heavy_stack_migrations")


@contextmanager
def as_postgres_migrations_staging():
    from heavy_stack.main_app import app

    app.config.SQL_DB_URL = pg_migration_staging_url
    yield
    app.config.SQL_DB_URL = prev_db_url


@contextmanager
def as_cockroach():
    from heavy_stack.main_app import app

    app.config.SQL_DB_URL = cockroach_url
    yield
    app.config.SQL_DB_URL = prev_db_url


def get_current_branch_name():
    branch_name = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).decode("utf-8").strip()
    return branch_name


def start_cockroachdb():
    return os.system("docker compose up --wait cockroach")


def run_existing_migrations_cockroach(retry_count=1):
    try:
        with as_cockroach():
            from alembic import command
            from alembic.config import Config

            alembic_cfg = Config("alembic.ini")

            command.upgrade(alembic_cfg, "head")
    except Exception:
        if retry_count <= 0:
            raise
        time.sleep(5)
        run_existing_migrations_cockroach(retry_count - 1)


def run_existing_migrations_postgres():
    with as_postgres_migrations_staging():
        from alembic import command
        from alembic.config import Config

        alembic_cfg = Config("alembic.ini")

        command.upgrade(alembic_cfg, "head")


def create_new_migrations(message: str):
    with as_postgres_migrations_staging():
        from alembic import command
        from alembic.config import Config

        alembic_cfg = Config("alembic.ini")

        command.revision(alembic_cfg, message=message, autogenerate=True)


def run_new_migrations():
    with as_postgres_migrations_staging():
        from alembic import command
        from alembic.config import Config

        alembic_cfg = Config("alembic.ini")

        command.upgrade(alembic_cfg, "head")
    with as_cockroach():
        from alembic import command
        from alembic.config import Config

        alembic_cfg = Config("alembic.ini")

        command.upgrade(alembic_cfg, "head")


def stop_cockroach():
    os.system("docker compose down cockroach")


def main(autoname: bool):
    if start_cockroachdb():
        print("Cockroach DB failed to start!")
        return
    cockroach_start = time.time()
    asyncio.run(create_db())
    try:
        try:
            run_existing_migrations_postgres()
        except Exception:
            print("Existing migrations (postgres) failed to run!")
            raise

        current_branch_name = get_current_branch_name()
        default_msg = f"migrations for {current_branch_name}"
        if not autoname:
            migration_message = input(f"Enter migration message ({default_msg}): ")
            migration_message = migration_message or default_msg
        else:
            migration_message = default_msg
        try:
            create_new_migrations(migration_message)
        except Exception:
            print("Could not create new migrations!")
            raise

        time_to_sleep = 15 - (time.time() - cockroach_start)
        if time_to_sleep > 0:
            print("Waiting for sufficient time for cockroach to create the DB and user")
            time.sleep(time_to_sleep)

        try:
            run_existing_migrations_cockroach()
        except Exception:
            print("Existing migrations (cockroach) failed to run!")
            raise
        try:
            run_new_migrations()
        except Exception:
            print("New migrations failed to run!")
            raise
    finally:
        stop_cockroach()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--auto-name", action="store_true")
    args = parser.parse_args()
    main(args.auto_name)
