from heavy_stack.config import get_config


def is_dev() -> bool:
    return get_config().ENVIRONMENT == "DEV"


def is_production() -> bool:
    return get_config().ENVIRONMENT == "PRODUCTION"
