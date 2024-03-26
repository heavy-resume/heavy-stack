import datetime

from zoneinfo import ZoneInfo

UTC = ZoneInfo("UTC")


def utc_now() -> datetime.datetime:
    return datetime.datetime.now(UTC)
