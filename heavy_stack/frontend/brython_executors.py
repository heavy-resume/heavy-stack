import uuid
from pathlib import Path
from typing import Any, Callable, cast

from reactpy import (
    component,
    create_context,
    html,
    use_context,
    use_ref,
    use_state,
)
from reactpy.core.events import EventHandler

from heavy_stack.frontend.reactpy_util import heavy_event

ScriptKey = str
BrythonModulePath = str
FunctionName = str
KeywordArgs = dict[str, Any]
ResultCallback = Callable | None
CompleteCallback = Callable


class BrythonExecutor:
    def __init__(self, brython_dir: Path):
        self._script_queue: list[tuple[ScriptKey, BrythonModulePath, FunctionName, KeywordArgs]] = []
        self._pending_scripts: list[tuple[ScriptKey, EventHandler]] = []
        self._brython_dir = str(brython_dir.absolute())
        self._function_to_brython_cache: dict[Callable, tuple[str, str]] = {}
        self._react_dispatch_function: Callable | None = None

    @staticmethod
    def get_head_elements(
        brython_pythonpath: str = "/static/brython",
        brython_url: str = "https://cdn.jsdelivr.net/npm/brython@3.12.3/brython.min.js",
        brython_library: str = "https://cdn.jsdelivr.net/npm/brython@3.12.3/brython_stdlib.js",
        debug: int = 1,
    ):
        return [
            html.script(
                {
                    "type": "text/javascript",
                    "src": brython_url,
                }
            ),
            html.script(
                {
                    "type": "text/javascript",
                    "src": brython_library,
                }
            ),
            html.script(
                {"type": "text/javascript"},
                "window.onload = function() {  brython({debug: "
                + str(debug)
                + ", pythonpath: ['"
                + brython_pythonpath
                + "']}); }",
            ),
        ]

    def assign_dispatch(self, dispatch: Callable):
        self._react_dispatch_function = dispatch

    def remove_pending_script(self, key: ScriptKey) -> None:
        self._pending_scripts = [(k, result_callback) for k, result_callback in self._pending_scripts if k != key]

    def call(
        self, function: Callable, result_callback: Callable | None = None, **kwargs
    ) -> Any | None:  # make mypy happy if this is used in something like all(...)
        def completed_callback(e, *args, **kw):
            self.remove_pending_script(key)
            if result_callback:
                result_callback(e["target"]["value"], *args, **kw)

        key = uuid.uuid4().hex
        module, func_name = self._to_brython_location(function)
        self._script_queue.append((key, module, func_name, kwargs))
        self._pending_scripts.append((key, heavy_event(completed_callback, stop_propagation=True)))
        # triggers an update
        if self._react_dispatch_function:
            self._react_dispatch_function(uuid.uuid4().hex)
        return None  # get error about str not callable if this returns str, fyi

    def _to_brython_location(self, function: Callable) -> tuple[BrythonModulePath, FunctionName]:
        return function.__module__, function.__name__

    def process_script_queue(self):
        script_elements = []
        for key, module, function, kwargs in self._script_queue:
            script = f"""
from browser import document, window
from {module} import {function}

kwargs = {kwargs}

data_storage = document.getElementById("{key}")

def signal_complete(result = ""):
    data_storage.value = result
    event = window.Event.new("input")
    data_storage.dispatchEvent(event)

result = {function}(signal_complete, **kwargs)
"""
            script_elements.append(
                html.script(
                    {"type": "text/python", "id": f"script_{key}", "key": f"script_{key}"},
                    script,
                )
            )
        script_result_elements = [
            html.input({"style": "display: none", "id": key, "on_change": completed_callback})
            for key, completed_callback in self._pending_scripts
        ]

        assert len(script_elements) == len({k for k, *rest in self._script_queue}), [
            k for k, *rest in self._script_queue
        ]
        self._script_queue = []

        return script_elements, script_result_elements


BrythonExecutorContext = create_context(cast(BrythonExecutor, None))


@component
def BrythonExecutorProvider(brython_dir: Path, *children):
    be_ref = use_ref(cast(BrythonExecutor | None, None), server_only=True)
    if not (brython_executor := be_ref.current):
        be_ref.set_current(brython_executor := BrythonExecutor(brython_dir))

    return BrythonExecutorContext(
        BrythonExecutorComponent(brython_executor.assign_dispatch),
        *children,
        value=brython_executor,
        key="brython_executor",
    )


@component
def BrythonExecutorComponent(assign_exec_id: Callable):
    be_context = cast(BrythonExecutor | None, use_context(BrythonExecutorContext))
    exec_id, set_exec_id = use_state("init")
    assign_exec_id(set_exec_id)

    if not be_context:
        return html.div({"style": "display: hidden", "key": "BrythonExecutorParent"})

    script_elements, script_result_elements = be_context.process_script_queue()
    return html.div(
        {
            "style": "display: hidden",
            "id": "BrythonExecutorParent",
            "key": "BrythonExecutorParent",
        },
        html.div({"id": "script-holder"}, *script_elements),
        html.div({"id": "script-data"}, *script_result_elements),
    )
