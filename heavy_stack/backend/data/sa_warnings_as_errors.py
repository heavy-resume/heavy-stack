import warnings

from sqlalchemy.exc import SAWarning


def enable_sa_warnings_as_errors() -> None:
    # Turn cartesian product warning into an error
    warnings.filterwarnings(
        "error",
        category=SAWarning,
    )
    warnings.filterwarnings(
        "ignore",
        r"[\s\S]*session\.exec[\s\S]*",
        category=DeprecationWarning,
    )
