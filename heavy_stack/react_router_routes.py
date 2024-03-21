from reactpy import use_location
from reactpy_router import route, simple

from heavy_stack.frontend.common import OuterContainer
from heavy_stack.frontend.landing import LandingPage
from heavy_stack.frontend.other_page import OtherPage


def get_reactpy_routes():
    use_location()
    return simple.router(
        route("/", OuterContainer(LandingPage())),
        route("/other", OuterContainer(OtherPage())),
    )
