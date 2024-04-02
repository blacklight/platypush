import json
from dataclasses import dataclass, field
from queue import Queue
from threading import Event
from typing import Any, Optional, Union

from websocket import WebSocketApp

from ._common import DEFAULT_TIMEOUT


@dataclass
class MopidyTask:
    """
    A task to be executed by the Mopidy client.
    """

    id: int
    method: str
    args: dict = field(default_factory=dict)
    response: Optional[Any] = None
    response_ready: Event = field(default_factory=Event)
    response_queue: Queue = field(default_factory=Queue)

    def to_dict(self):
        return {
            "jsonrpc": "2.0",
            "id": self.id,
            "method": self.method,
            'params': self.args,
        }

    def __str__(self):
        return json.dumps(self.to_dict())

    def send(self, ws: WebSocketApp):
        assert ws, "Websocket connection not established"
        self.response_ready.clear()
        ws.send(str(self))

    def get_response(self, timeout: Optional[float] = DEFAULT_TIMEOUT) -> Any:
        ret = self.response_queue.get(timeout=timeout)
        if isinstance(ret, dict):
            ret = ret.get('result')

        return ret

    def put_response(self, response: Union[dict, Exception]):
        self.response = response
        self.response_ready.set()
        self.response_queue.put_nowait(response)

    def wait(self, timeout: Optional[float] = DEFAULT_TIMEOUT) -> bool:
        return self.response_ready.wait(timeout=timeout)

    def run(self, ws: WebSocketApp, timeout: Optional[float] = DEFAULT_TIMEOUT):
        self.send(ws)
        return self.get_response(timeout=timeout)
