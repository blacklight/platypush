import threading
import time

from platypush.bus.redis import RedisBus
from platypush.message.event.application import ApplicationStartedEvent


class FakeRedis:
    def __init__(self):
        self.published = []
        self.closed = False

    def publish(self, queue, msg):
        self.published.append((queue, msg))

    def close(self):
        self.closed = True


class FakePubSub:
    def __init__(self, bus, messages=None):
        self.bus = bus
        self.messages = list(messages or [])
        self.closed = False
        self.subscribed = []
        self.unsubscribed = []
        self.get_message_calls = []

    def subscribe(self, queue):
        self.subscribed.append(queue)

    def get_message(self, *, ignore_subscribe_messages, timeout):
        self.get_message_calls.append(
            {
                'ignore_subscribe_messages': ignore_subscribe_messages,
                'timeout': timeout,
            }
        )

        if self.messages:
            return self.messages.pop(0)

        self.bus.stop()
        return None

    def listen(self):
        raise AssertionError('RedisBus.poll should not use blocking listen()')

    def unsubscribe(self, queue):
        self.unsubscribed.append(queue)

    def close(self):
        self.closed = True


def test_redis_bus_poll_uses_bounded_pubsub_polling():
    bus = RedisBus(redis_queue='test/bus')
    fake_redis = FakeRedis()
    fake_pubsub = FakePubSub(bus)
    bus._redis = fake_redis
    bus._pubsub = fake_pubsub

    bus.poll()

    assert fake_pubsub.subscribed == ['test/bus']
    assert fake_pubsub.closed
    assert fake_pubsub.get_message_calls == [
        {
            'ignore_subscribe_messages': True,
            'timeout': RedisBus._PUBSUB_POLL_TIMEOUT,
        }
    ]
    assert RedisBus._PUBSUB_POLL_TIMEOUT <= 0.1
    assert fake_redis.published


def test_redis_bus_poll_processes_messages():
    received = []
    received_event = threading.Event()
    bus = RedisBus(
        redis_queue='test/bus',
        on_message=lambda msg: (received.append(msg), received_event.set()),
    )
    event = ApplicationStartedEvent()
    fake_pubsub = FakePubSub(
        bus,
        messages=[
            {
                'type': 'message',
                'data': str(event).encode('utf-8'),
            }
        ],
    )
    bus._redis = FakeRedis()
    bus._pubsub = fake_pubsub

    bus.poll()
    received_event.wait(timeout=2)

    assert len(received) == 1
    assert isinstance(received[0], ApplicationStartedEvent)


def test_redis_bus_poll_stops_cleanly():
    """
    The consumer loop should not block indefinitely when the bus is stopped.
    """

    class SlowPubSub(FakePubSub):
        def get_message(self, *, ignore_subscribe_messages, timeout):
            self.get_message_calls.append(
                {
                    'ignore_subscribe_messages': ignore_subscribe_messages,
                    'timeout': timeout,
                }
            )
            return None

    bus = RedisBus(redis_queue='test/bus')
    bus._redis = FakeRedis()
    bus._pubsub = SlowPubSub(bus)

    poll_thread = threading.Thread(target=bus.poll)
    poll_thread.start()
    time.sleep(0.05)
    bus.stop()
    poll_thread.join(timeout=1)

    assert not poll_thread.is_alive()
