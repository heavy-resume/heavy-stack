import datetime
import logging
import os
from pathlib import Path
from typing import Any

from pydantic import BaseModel
from reactpy.core.state_recovery import StateRecoveryManager

from heavy_stack.shared_models.users import User

if os.environ.get("HR_ENVIRONMENT") == "PRODUCTION":
    import sys

    # for cockroachdb this spits error messages. Production doesn't need alembic anyways.
    sys.modules["alembic"] = {}  # type: ignore # don't import alembic

if os.environ.get("HEAVY_STACK_DO_DATA_RECORDING", "0") in ("1", "True", "true", "yes"):
    DO_DATA_RECORDING = True
else:
    DO_DATA_RECORDING = False

from reactpy import component, html
from reactpy.backend.sanic import Options, configure
from sanic_cors import CORS  # type: ignore

from heavy_stack.config import get_config
from heavy_stack.frontend.brython_executors import BrythonExecutor, BrythonExecutorProvider
from heavy_stack.frontend.timezones import TimezoneProvider
from heavy_stack.frontend.types import Component
from heavy_stack.main_app import app
from heavy_stack.middleware import register_db_middleware, register_heavy_request_middleware
from heavy_stack.react_router_routes import get_reactpy_routes

# block reactpy warning
logger = logging.getLogger("reactpy.backend.sanic")

# Set the logging level to ERROR, which is higher than WARNING
logger.setLevel(logging.ERROR)

# Define a new logging format that includes logger name and module name
log_format = (
    "[%(asctime)s] [%(process)d] [%(levelname)s] [%(name)s] [%(module)s] [%(pathname)s:%(lineno)d]:\n...%(message)s"
)

# Configure the logging system to use this format
logging.basicConfig(format=log_format, level=logging.INFO)


@component
def Main() -> Component:
    return BrythonExecutorProvider(Path("./brython"), TimezoneProvider(get_reactpy_routes()))


config = get_config()

env = get_config().ENVIRONMENT
assert env in ("DEV", "PRODUCTION"), f"Invalid environment: {env}"
if env != "PRODUCTION":
    title = f"Heävy Stack - {env}"
else:
    title = "Heävy Stack"

head = (
    html.title(title),
    html.meta({"name": "viewport", "content": "width=device-width, initial-scale=0.75"}),
    html.link({"rel": "icon", "href": "/static/images/favico.png", "type": "image/png"}),
    html.link({"rel": "stylesheet", "href": "/static/palette.css"}),
    html.link({"rel": "stylesheet", "href": "/static/fonts.css"}),
    html.link({"rel": "stylesheet", "href": "/static/common.css"}),
    html.link({"rel": "stylesheet", "href": "/static/input-components.css"}),
    BrythonExecutor.get_head_elements(),
)

cors_options = {"origins": config.CORS_HEADER.split(",")}


def default_serializer(obj: Any) -> Any:
    try:
        if isinstance(obj, BaseModel):
            return obj.dict()
    except Exception:
        logger.exception("Failed to serialize object")
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")


state_recovery_manager = StateRecoveryManager(
    serializable_types=[dict, User],
    pepper="change-me-to-something-else",
    default_serializer=default_serializer,
    deserializer_map={
        datetime.datetime: lambda dt: datetime.datetime.fromisoformat(dt),
    },
)
if DO_DATA_RECORDING:
    from tests.data_recording.socket_data_recorder import monkeypatch_in_socket_data_layer

    data_sends, data_recvs = monkeypatch_in_socket_data_layer()

configure(app, Main, Options(head=head, cors=cors_options), state_recovery_manager)
CORS(app, **cors_options)
app.config["CORS_AUTOMATIC_OPTIONS"] = True

app.static("/static", "./static", name="static_files")
app.static("/static/js", "./dist", name="js_bundles")
app.static("/static/brython", "./brython", name="brython_files")

register_db_middleware(app)
register_heavy_request_middleware(app)


if __name__ == "__main__":
    try:
        app.run(port=8000, access_log=False, single_process=True, workers=1)
    finally:
        if DO_DATA_RECORDING:
            import json

            sends = [("send", conn_id, ts, data) for conn_id, ts, data in data_sends]
            recvs = [("recv", conn_id, ts, data) for conn_id, ts, data in data_recvs]
            by_ts = sorted(sends + recvs, key=lambda x: x[2])
            with Path("data_recording.json").open("w") as file:
                json.dump(by_ts, file)
