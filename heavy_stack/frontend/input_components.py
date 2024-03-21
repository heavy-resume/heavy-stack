from typing import Callable
from uuid import uuid4

from reactpy import component, html, use_ref

from heavy_stack.frontend.reactpy_util import heavy_event
from heavy_stack.frontend.types import Component


@component
def LineInput(value: str, on_change: Callable = lambda e: None, **props) -> Component:
    return html.input(
        {
            "class_name": "line-input",
            "value": value,
            "on_click": heavy_event(lambda e: None, stop_propagation=True, prevent_default=True),
            "on_change": heavy_event(on_change),
            **props,
        }
    )


@component
def TextInput(value: str = "", on_change: Callable = lambda e: None, **props) -> Component:
    js_id = use_ref(uuid4().hex)

    return html.textarea(
        {
            "class_name": "line-input",
            "value": value,
            "on_click": heavy_event(lambda e: None, stop_propagation=True, prevent_default=True),
            "on_change": heavy_event(on_change),
            "id": js_id.current,
            **props,
        }
    )


@component
def NumberInput(value: int | float, on_change: Callable = lambda e: None, float_step="0.1") -> Component:
    return html.input(
        {
            "class_name": "line-input",
            "type": "number",
            "step": "1" if isinstance(value, int) else float_step,
            "value": value,
            "on_click": heavy_event(lambda e: None, stop_propagation=True, prevent_default=True),
            "on_change": heavy_event(on_change),
        }
    )


@component
def Button(label: str, on_click: Callable = lambda e: None, submit=False, style_classes=tuple(), **props) -> Component:
    return html.button(
        {
            "class_name": " ".join(style_classes + ("button",)),
            "type": "submit" if submit else "button",
            "on_click": heavy_event(on_click, stop_propagation=True),
            **props,
        },
        label,
    )
