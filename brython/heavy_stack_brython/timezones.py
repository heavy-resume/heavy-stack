import json

from reactpy_bridge import called_from_reactpy

try:
    from browser import window  # type: ignore
except ImportError:
    pass


@called_from_reactpy
def get_timezone_name_and_offset() -> str:
    js_date = window.Date.new()
    timezone_name = js_date.toLocaleTimeString("en-us", {"timeZoneName": "short"}).split(" ")[-1]
    timezone_offset = -js_date.getTimezoneOffset() / 60
    return json.dumps([timezone_name, timezone_offset])
