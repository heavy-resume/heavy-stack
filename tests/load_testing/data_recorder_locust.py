import json
import random
import time
from pathlib import Path

from locust import task
from locust_plugins.users.socketio import SocketIOUser


class DataRecorderUser(SocketIOUser):
    data_recording_file = Path(__file__).parent / "data_recording_demo.json"
    connection_id = 140526785495952
    user_action_range_min = 0.5
    user_action_range_max = 1
    do_loop = True

    def on_start(self) -> None:
        self.data_recording = sorted(
            [x for x in json.loads(self.data_recording_file.read_text()) if x[1] == self.connection_id],
            key=lambda x: x[2],
        )
        self.position = 0
        self._do_finish = False
        self._prev_send: float | None = None
        return super().on_start()

    @task
    def make_reactpy_connection(self):
        while True:
            self.connect("ws://localhost:8000/_reactpy/stream")

            while True:
                time.sleep(0.02)
                if self._do_finish:
                    break
            if self.do_loop:
                # try to avoid outrunning the server  (Cannot receive from websocket interface after it is closed.)
                time.sleep(1)

                self.ws_greenlet.kill()
                self.ws.close()
                self.position = 0
                self._do_finish = False
            else:
                self.stop()
                return

    def _send(self, data: dict) -> None:
        time.sleep(
            random.randrange(int(self.user_action_range_min * 1000), int(self.user_action_range_max * 1000)) / 1000.0
        )
        if data.get("timeStamp"):
            data["timeStamp"] = time.time()
        data_to_send = json.dumps(data)
        # print(f"sending {data_to_send}")
        self.send(data_to_send, name="msg")
        self._prev_send = time.time()
        self.position += 1

    def on_message(self, message) -> None:
        # print(f"Got msg: {message}")
        if not message:
            return

        if self._prev_send:
            # Record the successful request
            self.environment.events.request.fire(
                request_type="WebSocket",
                name="server response",
                response_time=(time.time() - self._prev_send) * 1000.0,
                response_length=len(message),
            )
            self._prev_send = None

        message_data = json.loads(message)
        if message_data["type"] == self.data_recording[self.position][3]["type"]:
            self.position += 1
            # recv means server received from client. We are the client so send
            while self.position < len(self.data_recording) and self.data_recording[self.position][0] == "recv":
                self._send(self.data_recording[self.position][3])
        else:
            print(f"Ignoring message: {self.data_recording[self.position][3]['type']}")
        if self.position == len(self.data_recording):
            self._do_finish = True
