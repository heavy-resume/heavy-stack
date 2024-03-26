from dataclasses import dataclass
from typing import Literal, cast

from reactpy.backend.sanic import use_request
from sanic import Request
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

from heavy_stack.backend.data.db_connection import (
    close_current_db_session,
    set_current_db_session,
)
from heavy_stack.backend.data.model_managers.user_managers import UserManager
from heavy_stack.backend.data.model_mungers.user_model_mungers import UserModelMunger
from heavy_stack.backend.sessions import get_user_id, retrieve_session
from heavy_stack.shared_models.users import AnonymousUser, User, UserId


@dataclass
class HeavyContext:
    is_heavy: Literal[True]
    db_session: AsyncSession | None
    db_sessionmaker: sessionmaker
    user_id: UserId | None
    user: User


class HeavyRequest(Request):
    ctx: HeavyContext


async def prepare_request(request: Request) -> HeavyRequest:
    if getattr(request.ctx, "is_heavy", False):
        return cast(HeavyRequest, request)
    request = cast(HeavyRequest, request)
    db_session: AsyncSession = request.ctx.db_sessionmaker()
    token = set_current_db_session(db_session)
    try:
        request.ctx.is_heavy = True
        request.ctx.user_id = user_id = await get_user_id(db_session, request)
        request.ctx.user = AnonymousUser
        if not user_id:
            return request
        session = await retrieve_session(request)
        if session and user_id:
            user_manager = UserManager(UserModelMunger())
            user = await user_manager.get_user(user_id)
            request.ctx.user = user
    finally:
        await close_current_db_session(token)
    return request


def use_heavy_request() -> HeavyRequest:
    return cast(HeavyRequest, use_request())


def get_heavy_context(request: Request) -> HeavyContext:
    result = cast(HeavyContext, request.ctx)
    assert result.is_heavy
    return result
