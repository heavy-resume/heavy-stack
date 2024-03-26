# monkey patch in socket data layer

import time
from typing import Any

from reactpy.backend.sanic import _make_send_recv_callbacks as _make_send_recv_callbacks_orig
from reactpy.core.serve import RecvCoroutine
from sanic.server.websockets.connection import WebSocketConnection

from custom_reactpy.reactpy.core.serve import SendCoroutine

connection_id = int
timestamp = float
payload = str


def monkeypatch_in_socket_data_layer() -> (
    tuple[list[tuple[connection_id, timestamp, dict]], list[tuple[connection_id, timestamp, dict]]]
):
    data_sends: list[tuple[connection_id, timestamp, dict]] = []
    data_recvs: list[tuple[connection_id, timestamp, dict]] = []

    def new_make_send_recv_callbacks(
        socket: WebSocketConnection,
    ) -> tuple[SendCoroutine, RecvCoroutine]:
        sock_send, sock_recv = _make_send_recv_callbacks_orig(socket)

        async def new_send(value: Any) -> None:
            data_sends.append((id(socket), time.time(), value))
            await sock_send(value)

        async def new_recv():
            result = await sock_recv()
            data_recvs.append((id(socket), time.time(), result))
            return result

        return new_send, new_recv

    from reactpy.backend import sanic

    sanic._make_send_recv_callbacks = new_make_send_recv_callbacks

    return data_sends, data_recvs
