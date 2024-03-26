try:
    from browser import document
except ImportError:
    pass

from reactpy_bridge import called_from_reactpy


@called_from_reactpy
def set_session_lived_cookie(cookie_name: str, cookie_value: str):
    document.cookie = f"{cookie_name}={cookie_value}; path=/; SameSite=Strict; Secure"
