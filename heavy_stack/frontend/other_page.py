from reactpy import component, html

from heavy_stack.frontend.basic_components import RouterLink, paragraph
from heavy_stack.frontend.types import Component


@component
def OtherPage() -> Component:
    return html.div(
        paragraph("This is another page"),
        RouterLink("Go back", to="/"),
    )
