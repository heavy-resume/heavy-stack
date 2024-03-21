from functools import wraps
from typing import Any, Callable, Concatenate, ParamSpec

P = ParamSpec("P")


def called_from_reactpy(
    func: Callable[P, Any], include_result_callback: bool = False
) -> Callable[Concatenate[Callable, P], Any]:
    @wraps(func)
    def wrapper(signal_complete: Callable, *args: P.args, **kwargs: P.kwargs) -> Any:
        if include_result_callback:
            return func(signal_complete, *args, **kwargs)  # type: ignore
        signal_complete(result := func(*args, **kwargs))
        return result

    return wrapper
