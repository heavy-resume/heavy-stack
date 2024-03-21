import datetime
import json
from logging import getLogger
from typing import cast

from heavy_stack_brython.timezones import get_timezone_name_and_offset
from reactpy import component, create_context, html, use_context, use_state

from heavy_stack.frontend.brython_executors import BrythonExecutorContext
from heavy_stack.frontend.reactpy_util import heavy_use_effect

TimezoneContext = create_context(cast(datetime.timezone, None))

logger = getLogger(__name__)


@component
def TimezoneProvider(*children):
    brython_executor = use_context(BrythonExecutorContext)
    user_timezone, set_user_timezone = use_state(None)

    def assign_user_timezone(timezone_name: str, timezone_offset: float) -> None:
        nonlocal user_timezone
        if user_timezone is not None:
            return
        try:
            offset = datetime.timedelta(hours=timezone_offset)
            user_timezone = datetime.timezone(offset, name=timezone_name)
        except Exception:
            # default to UTC
            logger.warning(
                f"Failed to create timezone {timezone_name} with offset {timezone_offset}. Defaulting to UTC."
            )
            user_timezone = datetime.timezone(offset=0, name="UTC")
        set_user_timezone(user_timezone)

    heavy_use_effect(
        lambda: brython_executor.call(
            get_timezone_name_and_offset,
            lambda v: assign_user_timezone(*(json.loads(v[:200]))),
        )
    )
    if not user_timezone:
        return html.div()

    return TimezoneContext(*children, value=user_timezone, key="user_timezone")


def to_user_timezone(dt: datetime.datetime) -> datetime.datetime | None:
    user_timezone = use_context(TimezoneContext)

    return dt.astimezone(user_timezone)
