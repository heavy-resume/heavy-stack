import asyncio
import inspect
import logging
from functools import wraps
from types import EllipsisType
from typing import Any, Callable, Sequence

from reactpy import event, use_effect
from reactpy.core.hooks import _try_to_infer_closure_values

from heavy_stack.backend.api_requests import HeavyContext, use_heavy_request
from heavy_stack.backend.data.db_connection import (
    close_current_db_session,
    set_current_db_session,
)

logger = logging.getLogger("reactpy.use_effect")


def heavy_use_effect(func: Callable, deps: Sequence[Any] | EllipsisType | None = ...) -> None:
    if deps is ...:
        if asyncio.iscoroutinefunction(func):
            # if a coroutine, then probably just want to run once, not every render, if no deps
            deps = []
        else:
            deps = _try_to_infer_closure_values(func, deps)
            # if a function is a dependency in the closure then risk of infinite loop
            deps = [x for x in deps if not inspect.isfunction(x)] if deps is not None else None
    return heavy_wrapper_common("use_effect", use_effect, func, deps)


def heavy_wrapper_common(wrapped_func_name: str, wrapped_func: Callable, func: Callable | Any, *args, **kwargs):
    if inspect.iscoroutinefunction(func):
        request = use_heavy_request()

        @wraps(func)
        async def inner(*args, **kwargs) -> None:
            try:
                request_ctx = request.ctx
                db_session = request_ctx.db_sessionmaker()
                token = set_current_db_session(db_session)
                heavy_context = HeavyContext(
                    is_heavy=True,
                    db_session=db_session,
                    db_sessionmaker=request_ctx.db_sessionmaker,
                    user_id=request_ctx.user_id,
                    user=request_ctx.user,
                )

                return await func(heavy_context, *args, **kwargs)
            except Exception:
                logger.exception(f"Error in {wrapped_func_name}")
                raise
            finally:
                await close_current_db_session(token)

    else:

        @wraps(func)
        def inner(*args, **kwargs) -> None:
            try:
                return func(*args, **kwargs)
            except Exception:
                logger.exception(f"Error in {wrapped_func_name}")
                raise

    return wrapped_func(inner, *args, **kwargs)


# monkey patch use_effect to break it
import reactpy  # noqa: E402


def use_heavy_use_effect(*args, **kwargs):
    raise Exception("Use heavy_use_effect instead of use_effect")


reactpy.use_effect = use_heavy_use_effect


def heavy_event(
    function: Callable[..., Any] | None = None,
    *,
    stop_propagation: bool = False,
    prevent_default: bool = False,
) -> Any:
    if __debug__:
        assert function is None or callable(function)
    return heavy_wrapper_common(
        "event",
        event,
        function,
        stop_propagation=stop_propagation,
        prevent_default=prevent_default,
    )


def use_heavy_event(*args, **kwargs):
    raise Exception("Use heavy_event instead of event")


reactpy.event = use_heavy_event
