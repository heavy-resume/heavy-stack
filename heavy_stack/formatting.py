import datetime
from typing import cast

from heavy_stack.frontend.timezones import to_user_timezone
from heavy_stack.frontend.types import Component


def date_time_str(time: datetime.datetime) -> str:
    return cast(datetime.datetime, to_user_timezone(time)).strftime("%m/%d/%Y %I:%M:%S %p %Z")


def date_time_str_or_never(time: datetime.datetime | None) -> Component | str:
    if time is None:
        return "Never"
    return date_time_str(time)
