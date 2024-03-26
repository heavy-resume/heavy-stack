import datetime
from typing import cast

from heavy_stack_brython.navigate import open_new_tab
from heavy_stack_brython.scrolling import scroll_to_element
from reactpy import component, html, use_context, use_state

from heavy_stack.backend.api_requests import HeavyContext
from heavy_stack.backend.data.model_managers.user_managers import UserManager
from heavy_stack.backend.data.model_mungers.user_model_mungers import UserModelMunger
from heavy_stack.formatting import date_time_str, date_time_str_or_never
from heavy_stack.frontend.basic_components import (
    CenteredColumn,
    ExpandableSection,
    PageTitle,
    RouterLink,
    Section,
    Spacer,
    paragraph,
    preformatted,
)
from heavy_stack.frontend.brython_executors import BrythonExecutorContext
from heavy_stack.frontend.input_components import Button, LineInput, NumberInput
from heavy_stack.frontend.reactpy_util import heavy_event, heavy_use_effect
from heavy_stack.frontend.types import Component
from heavy_stack.shared_models.users import AnonymousUser, User
from heavy_stack.time_util import utc_now


@component
def LandingPage() -> Component:
    user, set_user = use_state(cast(User | None, None))
    right_now, set_right_now = use_state(utc_now())
    button_press_time, set_button_press_time = use_state(cast(datetime.datetime | None, None))
    input_value, set_input_value = use_state("")

    brython_executor = use_context(BrythonExecutorContext)

    async def get_user(heavy_context: HeavyContext) -> None:
        # async functions can access the database
        user = await UserManager(UserModelMunger()).get_user("1234")
        if user:
            set_user(user)
        else:
            set_user(AnonymousUser)

    heavy_use_effect(get_user)

    return html.div(
        PageTitle("Landing Page"),
        html.h1("Time (press button below to update):"),
        html.h1({"id": "time-at-top"}, f"{date_time_str(right_now)}"),
        Section(
            html.h2("This is a section"),
        ),
        ExpandableSection(
            html.h2("This is an expandable section"),
            expanded_children=[html.h3("This is the expanded children!"), html.p("Click again to close")],
        ),
        ExpandableSection(
            html.h2("This section is one-way!"),
            expanded_children=[Section("Nested section"), html.div("Number input: ", NumberInput(0))],
            one_way=True,
        ),
        Section(
            html.h3(f"Button last pressed: {date_time_str_or_never(button_press_time)}"),
            Button("Update time", on_click=lambda e: set_right_now(utc_now()) or set_button_press_time(utc_now())),
            Section(
                CenteredColumn(
                    html.p("Centered column"),
                    html.form(
                        {
                            "on_submit": heavy_event(
                                lambda e: set_input_value(e["target"]["elements"][0]["value"]),
                                stop_propagation=True,
                                prevent_default=True,
                            )
                        },
                        html.div(
                            LineInput(""),
                        ),
                        Spacer(),
                        html.div(
                            Button("Update value", submit=True),
                        ),
                    ),
                    Spacer(),
                    paragraph(f"Input value is: {input_value}"),
                )
            ),
        ),
        Section("Current user is AnonymousUser" if user == AnonymousUser else "Current user isn't set yet"),
        Section(
            preformatted(
                """
                preformatted text goes in preformatted(...)

                This generally is ugly but might be suitable for legal docs, code, or other things.
                """
            )
        ),
        Section(
            CenteredColumn(
                Button(
                    "Scroll to time using the Brython Executor",
                    on_click=lambda e: brython_executor.call(scroll_to_element, delay=0, js_id="time-at-top"),
                ),
                Spacer(),
                Button(
                    "Use Brython to open the Heavy Stack github in a new tab",
                    on_click=lambda e: brython_executor.call(
                        open_new_tab, url="https://github.com/heavy-resume/heavy-stack"
                    ),
                ),
                Spacer(),
                RouterLink("Go to another page", style_classes=("button",), to="/other"),
            )
        ),
    )
