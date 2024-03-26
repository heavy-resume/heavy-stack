from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

from heavy_stack.backend.api_requests import prepare_request
from heavy_stack.backend.data.db_connection import create_db_engine
from heavy_stack.config import get_config

config = get_config()

bind = create_db_engine()


# must be called first
def register_db_middleware(app) -> None:
    _sessionmaker: sessionmaker = sessionmaker(  # type: ignore
        bind=bind,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    @app.middleware("request")
    async def inject_sessionmaker(request):
        request.ctx.db_sessionmaker = _sessionmaker


def register_heavy_request_middleware(app) -> None:
    @app.middleware("request")
    async def inject_heavy_request(request):
        await prepare_request(request)
