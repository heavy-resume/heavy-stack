from sqlmodel.ext.asyncio.session import AsyncSession

from heavy_stack.backend.data.db_connection import get_current_db_session


class SQLRepositoryBase:
    def __init__(self, session: AsyncSession | None = None) -> None:
        self._db_session = session or get_current_db_session()
