from reactpy import component, html

from heavy_stack.frontend.types import Component


@component
def OuterContainer(inner) -> Component:
    # when using router links this is hidden for a moment
    # can also put meta elements like nav bar here
    return html.section(
        {"class_name": "main-container"},
        *(
            [
                html.div(
                    {"id": "outer-container-contents", "class": "outer-container-contents"},
                    inner,
                )
            ]
        ),
    )
