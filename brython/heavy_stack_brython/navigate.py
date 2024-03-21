from reactpy_bridge import called_from_reactpy

try:
    from browser import aio, window  # type: ignore
except ImportError:
    pass


@called_from_reactpy
def navigate_to(url: str):
    window.location.href = url


@called_from_reactpy
def open_new_tab(url: str):
    window.open(url, "_blank")


@called_from_reactpy
def short_hide_outer_container_contents():
    window.document.getElementById("outer-container-contents").style.display = "none"

    async def show_again():
        await aio.sleep(0.2)
        window.document.getElementById("outer-container-contents").style = ""

    aio.run(show_again())
