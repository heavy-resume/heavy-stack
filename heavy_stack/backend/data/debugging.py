from sqlmodel.ext.asyncio.session import AsyncSession

from heavy_stack.backend.data.db_connection import get_current_db_session


def get_filled_in_query(query, session: AsyncSession | None = None):
    session = session or get_current_db_session()
    return query.compile(session.bind, compile_kwargs={"literal_binds": True})
