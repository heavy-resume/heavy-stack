try:
    from browser import window
except ImportError:
    pass

from reactpy_bridge import called_from_reactpy


@called_from_reactpy
def set_session_storage(key: str, value: str):
    window.sessionStorage.setItem(key, value)
