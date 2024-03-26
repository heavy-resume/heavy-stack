from reactpy_bridge import called_from_reactpy

try:
    from browser import document  # type: ignore
except ImportError:
    pass


@called_from_reactpy
def click_element(js_id):
    element = document[js_id]
    element.click()
