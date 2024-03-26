from reactpy_bridge import called_from_reactpy

try:
    from browser import document, window  # type: ignore
except ImportError:
    pass


@called_from_reactpy
def scroll_to_element(js_id, delay=300, position="center"):
    def scroll():
        document[js_id].scrollIntoView({"behavior": "smooth", "block": position})

    window.setTimeout(scroll, delay)


@called_from_reactpy
def scroll_to_top():
    window.scrollTo({"top": 0})
