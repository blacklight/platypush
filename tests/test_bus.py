import threading
import time
from unittest.mock import MagicMock, patch

from platypush.bus import Bus
from platypush.message.event import Event


class FakeEvent(Event):
    pass


class FakeExecutor:
    """A fake executor that records submissions and can run them synchronously."""

    def __init__(self, run_sync=False):
        self.submitted = []
        self.run_sync = run_sync

    def submit(self, fn, *args, **kwargs):
        self.submitted.append((fn, args, kwargs))
        if self.run_sync:
            return fn(*args, **kwargs)
        future = MagicMock()
        return future


def test_bus_processes_message_without_spawning_thread():
    received = []
    bus = Bus()
    bus._executor = FakeExecutor(run_sync=True)

    def handler(msg):
        received.append(msg)

    bus.register_handler(FakeEvent, handler)
    msg = FakeEvent()
    bus._msg_executor(msg)

    assert len(received) == 1
    assert received[0] is msg


def test_bus_poll_stops_cleanly():
    bus = Bus(on_message=lambda msg: None)
    bus._executor = FakeExecutor()

    poll_thread = threading.Thread(target=bus.poll)
    poll_thread.start()
    time.sleep(0.1)
    bus.stop()
    poll_thread.join(timeout=2)

    assert not poll_thread.is_alive()


def test_bus_handler_exceptions_are_logged():
    bus = Bus()
    bus._executor = FakeExecutor(run_sync=True)

    def failing_handler(msg):
        raise RuntimeError('handler error')

    bus.register_handler(FakeEvent, failing_handler)

    with patch('platypush.bus.logger') as mock_logger:
        bus._msg_executor(FakeEvent())

    mock_logger.error.assert_called()
