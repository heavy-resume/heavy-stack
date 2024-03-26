from dataclasses import dataclass
from typing import Literal, cast

from heavy_stack.main_app import app as _app


@dataclass
class HeavyStackConfig:
    """
    The Heavy Stack configuration

    This is set via environment variables.
    All environment variables have the HR_ prefix to avoid collisions.

    So for example, HR_CORS_HEADER -> CORS_HEADER
    """

    ENVIRONMENT: Literal["DEV", "PRODUCTION"]
    CORS_HEADER: str
    REDIS_URL: str
    SQL_DB_URL: str
    VECTOR_DB_URL: str


def get_config() -> HeavyStackConfig:
    if not getattr(_app.config, "SQL_DB_URL", None):

        def mutate_config_from_secrets(app_config) -> None:
            import asyncio

            from heavy_stack.backend import secrets

            if app_config.ENVIRONMENT == "PRODUCTION":
                try:
                    secrets.get_secret
                except AttributeError:
                    # secrets model doesn't need these to be populated
                    pass
                else:

                    async def _mutate_config_from_secrets() -> None:
                        async def update_sql_db_url() -> None:
                            if not getattr(app_config, "SQL_DB_URL", None):
                                _, secret_value = await secrets.get_secret(secrets.Secrets.COCKROACH_DB_URL)
                                app_config.SQL_DB_URL = "cockroachdb+asyncpg://" + secret_value.strip() + "?ssl=require"

                        async def update_vector_db_url() -> None:
                            if not getattr(app_config, "VECTOR_DB_URL", None):
                                _, secret_value = await secrets.get_secret(secrets.Secrets.SUPABASE_DB_URL)
                                app_config.VECTOR_DB_URL = (
                                    "postgresql+asyncpg://" + secret_value.strip() + "?ssl=verify-full"
                                )

                        await asyncio.gather(update_sql_db_url(), update_vector_db_url())

                    loop = asyncio.new_event_loop()
                    task = loop.create_task(_mutate_config_from_secrets())
                    loop.run_until_complete(task)
            else:
                raise Exception("SQL_DB_URL is not set in the environment.")

        mutate_config_from_secrets(_app.config)
    return cast(HeavyStackConfig, _app.config)
