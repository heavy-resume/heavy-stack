import json
import uuid
from dataclasses import asdict, dataclass, field

from cachetools import TTLCache
from sanic import HTTPResponse, Request, text
from sqlmodel.ext.asyncio.session import AsyncSession

from heavy_stack.auth.cookies import SESSION_COOKIE
from heavy_stack.backend.redis_util import redis_client
from heavy_stack.shared_models.users import UserId

SessionId = str

SESSION_LENGTH = 60 * 60 * 48


@dataclass
class SessionData:
    user_id: str
    session_id: SessionId = field(default_factory=lambda: uuid.uuid4().hex)


session_cache: TTLCache[SessionId, SessionData] = TTLCache(maxsize=100, ttl=60)


async def create_session(user_id: str, pw_hash_derived_key: bytes) -> SessionData:
    session_data = SessionData(
        user_id=user_id,
    )
    client = redis_client()
    await client.setex(session_data.session_id, SESSION_LENGTH, json.dumps(asdict(session_data)))
    return session_data


async def get_session(session_id: SessionId) -> SessionData | None:
    if not session_id:
        return None
    if cached_session := session_cache.get(session_id):
        return cached_session

    client = redis_client()
    data = await client.get(session_id)
    if not data:
        return None
    return SessionData(**json.loads(data))


def set_session_cookie(session_id: SessionId) -> HTTPResponse:
    response = text("")
    response.add_cookie(SESSION_COOKIE, session_id, path="/", max_age=SESSION_LENGTH)
    return response


async def delete_session(session_id: SessionId) -> None:
    client = redis_client()
    await client.delete(session_id)


async def retrieve_session(request: Request):
    session_id = request.cookies.get(SESSION_COOKIE)
    if not session_id:
        return None
    session_data = await get_session(session_id)
    return session_data


async def get_user_id(db_session: AsyncSession, request: Request) -> UserId | None:
    # implement your own logic
    return None
