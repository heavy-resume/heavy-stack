import textwrap
from functools import lru_cache
from typing import Callable, Sequence
from uuid import uuid4

from heavy_stack_brython.events import click_element
from heavy_stack_brython.navigate import open_new_tab, short_hide_outer_container_contents
from heavy_stack_brython.scrolling import scroll_to_top
from reactpy import component, html, use_context, use_state
from reactpy_router import link

from heavy_stack.frontend.brython_executors import BrythonExecutorContext
from heavy_stack.frontend.reactpy_util import heavy_event
from heavy_stack.frontend.types import Component


@component
def Section(*children: Component, style_classes: tuple[str, ...] = tuple()) -> Component:
    return html.section({"class_name": " ".join(style_classes + ("section",))}, *children)


@component
def ExpandableSection(
    *children: Component,
    expanded_children: Sequence[Component] | None = None,
    style_classes: tuple[str] | None = None,
    start_expanded: bool = False,
    expand_hook: Callable | None = None,
    attrs: dict | None = None,
    one_way: bool = False,
) -> Component:
    expanded, set_expanded = use_state(start_expanded)
    expanded_children = expanded_children or []
    base_class_names: tuple[str, ...]
    if expanded_children:
        if expanded:
            if one_way:
                base_class_names = ("section",)
            else:
                base_class_names = ("expandable-section", "section")
        else:
            base_class_names = ("not-expanded-section", "expandable-section", "section")
    else:
        base_class_names = ("section",)
    extra: Sequence[Component] = expanded_children if expanded else []

    def do_expand(e):
        set_expanded(not expanded)
        if expand_hook:
            expand_hook(e)

    return html.section(
        {
            "class_name": " ".join(base_class_names + (style_classes or tuple())),
            "on_click": (
                heavy_event(do_expand, prevent_default=True, stop_propagation=True)
                if not one_way or not expanded
                else ""
            ),
        }
        | (attrs or {}),
        *children,
        *extra,
    )


@component
def PageTitle(title: str) -> Component:
    return html.h1({"class_name": "page-title"}, title)


@lru_cache
def paragraph(text: str, style_classes: tuple[str] | None = None) -> Component:
    return html.p({"class_name": " ".join(style_classes or [])}, textwrap.dedent(text).strip())


@lru_cache
def preformatted(text: str, style_classes: tuple[str] | None = None) -> Component:
    return html.pre(
        {"class_name": " ".join(("preformatted",) + (style_classes or tuple()))},
        textwrap.dedent(text).strip(),
    )


@component
def RouterLink(*children, to, style_classes: tuple[str, ...] | None = None, reset_scroll=True) -> Component:
    brython_executor = use_context(BrythonExecutorContext)
    link_id, _ = use_state(uuid4().hex, server_only=False)

    def router_link(e: dict) -> None:
        if e.get("ctrlKey"):
            brython_executor.call(open_new_tab, url=to)
            return
        if reset_scroll:
            brython_executor.call(short_hide_outer_container_contents)
        brython_executor.call(click_element, js_id=link_id)
        if reset_scroll:
            brython_executor.call(scroll_to_top)

    _children = (
        html.span(
            {
                "class_name": "link-span",
                "on_click": heavy_event(router_link, stop_propagation=True, prevent_default=True),
            },
            *children,
        ),
    )
    return link(
        *_children,
        to=to,
        class_name=" ".join((style_classes or tuple()) + ("link",)),
        id=link_id,
    )


def _to_list_item(item: tuple[Component, ...] | Component) -> Component:
    if not isinstance(item, tuple):
        return html.li(item)
    else:
        if len(item) == 1:
            return html.li(item[0])
        return html.li(item[0], BulletedList(*item[1:]))


# @lru_cache
@component
def BulletedList(*items: tuple[Component, ...] | Component, style_classes: tuple[str] | None = None) -> Component:
    if len(items) == 1 and isinstance(items[0], str):
        items = tuple(textwrap.dedent(items[0]).strip().splitlines())
    return html.ul(
        {"class_name": " ".join(("bulleted-list",) + (style_classes or tuple()))},
        *[_to_list_item(item) for item in items],
    )


@component
def NewTabLink(href: str, *children, style_classes: tuple[str] | None = None) -> Component:
    children = children or (href,)
    return html.a(
        {
            "class_name": " ".join((style_classes or tuple()) + ("link",)),
            "href": href,
            "target": "_blank",
            "on_click": heavy_event(lambda e: None, stop_propagation=True),
        },
        *children,
    )


@component
def CenteredColumn(*children: Component, style_classes: tuple[str] | None = None) -> Component:
    return html.div({"class_name": " ".join((style_classes or tuple()) + ("centered-column",))}, *children)


@component
def Spacer() -> Component:
    return html.div({"class_name": "spacer"})


@component
def FlexRow(*children: Component, centered: bool = False, style_classes: tuple[str] | None = None) -> Component:
    return html.div(
        {
            "style": "justify-content: center" if centered else "",
            "class_name": " ".join((style_classes or tuple()) + ("flex-row",)),
        },
        *children,
    )
