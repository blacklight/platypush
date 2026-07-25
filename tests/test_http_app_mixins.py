from unittest.mock import MagicMock, patch

from platypush.backend.http.app.mixins import Message, PubSubMixin


class _FakePubSub:
    def __init__(self, responses):
        self.responses = list(responses)
        self.closed = False

    def subscribe(self, *channels):
        pass

    def get_message(self, *, ignore_subscribe_messages, timeout):
        if not self.responses:
            return None
        response = self.responses.pop(0)
        if isinstance(response, BaseException):
            raise response
        return response

    def close(self):
        self.closed = True


class _FakeRedis:
    def __init__(self, pubsub):
        self._pubsub = pubsub

    def pubsub(self):
        return self._pubsub


class _Mixin(PubSubMixin):
    def __init__(self):
        self._pubsub = None
        self._subscriptions = {'events'}
        self._pubsub_lock = MagicMock()


def test_listen_recovers_from_indexerror():
    """
    If redis-py returns a malformed short Pub/Sub response that raises
    IndexError, the listen loop must close the broken connection and
    continue delivering subsequent messages.
    """
    responses = [
        # First response is malformed and triggers an IndexError inside
        # redis.client.PubSub.handle_message.
        IndexError('list index out of range'),
        {'type': 'message', 'channel': b'events', 'data': b'hello'},
    ]
    pubsub = _FakePubSub(responses)
    mixin = _Mixin()

    with patch(
        'platypush.backend.http.app.mixins.get_redis',
        return_value=_FakeRedis(pubsub),
    ):
        gen = mixin.listen()
        msg = next(gen)

    assert isinstance(msg, Message)
    assert msg.channel == 'events'
    assert msg.data == b'hello'
    assert pubsub.closed


if __name__ == '__main__':
    import pytest

    pytest.main()
