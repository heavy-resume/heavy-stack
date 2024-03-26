from sanic import Sanic

app = Sanic("ReactMain", env_prefix="SETME_ENV_PREFIX_", configure_logging=False)
app.config.OAS = False  # disable OpenAPI
app.config.REQUEST_MAX_SIZE = 100000
app.config.WEBSOCKET_MAX_SIZE = 1000000
app.config.WEBSOCKET_PING_INTERVAL = 90
app.config.WEBSOCKET_PING_TIMEOUT = 30
