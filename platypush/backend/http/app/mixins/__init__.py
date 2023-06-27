from contextlib import contextmanager
from dataclasses import dataclass
import json
import logging
from multiprocessing import RLock
from typing import Generator, Iterable, Optional, Set, Union

from redis import ConnectionError as RedisConnectionError
from redis.client import PubSub

from platypush.config import Config
from platypush.message import Message as AppMessage
from platypush.utils import get_redis

logger = logging.getLogger(__name__)

MessageType = Union[AppMessage, bytes, str, dict, list, set, tuple]
"""Types of supported messages on Redis/websocket channels."""


@dataclass
class Message:
    """
    A wrapper for a message received on a Redis subscription.
    """

    data: bytes
    """The data received in the message."""
    channel: str
    """The channel the message was received on."""


class PubSubMixin:
    """
    A mixin for Tornado route handlers that support pub/sub mechanisms.
    """

    def __init__(self, *_, subscriptions: Optional[Iterable[str]] = None, **__):
        self._pubsub: Optional[PubSub] = None
        """Pub/sub proxy."""
        self._subscriptions: Set[str] = set(subscriptions or [])
        """Set of current channel subscriptions."""
        self._pubsub_lock = RLock()
        """
        Subscriptions lock. It ensures that the list of subscriptions is
        manipulated by one thread or process at the time.
        """

        self.subscribe(*self._subscriptions)

    @property
    @contextmanager
    def pubsub(self):
        """
        Pub/sub proxy lazy property with context manager.
        """
        with self._pubsub_lock:
            # Lazy initialization for the pub/sub object.
            if self._pubsub is None:
                self._pubsub = get_redis().pubsub()

        # Yield the pub/sub object (context manager pattern).
        yield self._pubsub

        with self._pubsub_lock:
            # Close and free the pub/sub object if it has no active subscriptions.
            if self._pubsub is not None and len(self._subscriptions) == 0:
                self._pubsub.close()
                self._pubsub = None

    @staticmethod
    def _serialize(data: MessageType) -> bytes:
        """
        Serialize a message as bytes before delivering it to either a Redis or websocket channel.
        """
        if isinstance(data, AppMessage):
            data = str(data)
        if isinstance(data, (list, tuple, set)):
            data = list(data)
        if isinstance(data, (list, dict)):
            data = json.dumps(data, cls=AppMessage.Encoder)
        if isinstance(data, str):
            data = data.encode('utf-8')

        return data

    @classmethod
    def publish(cls, data: MessageType, *channels: str) -> None:
        """
        Publish data on one or more Redis channels.
        """
        for channel in channels:
            get_redis().publish(channel, cls._serialize(data))

    def subscribe(self, *channels: str) -> None:
        """
        Subscribe to a set of Redis channels.
        """
        with self.pubsub as pubsub:
            for channel in channels:
                pubsub.subscribe(channel)
                self._subscriptions.add(channel)

    def unsubscribe(self, *channels: str) -> None:
        """
        Unsubscribe from a set of Redis channels.
        """
        with self.pubsub as pubsub:
            for channel in channels:
                if channel in self._subscriptions:
                    pubsub.unsubscribe(channel)
                    self._subscriptions.remove(channel)

    def listen(self) -> Generator[Message, None, None]:
        """
        Listens for pub/sub messages and yields them.
        """
        try:
            with self.pubsub as pubsub:
                for msg in pubsub.listen():
                    channel = msg.get('channel', b'').decode()
                    if msg.get('type') != 'message' or not (
                        channel and channel in self._subscriptions
                    ):
                        continue

                    yield Message(data=msg.get('data', b''), channel=channel)
        except (AttributeError, RedisConnectionError):
            return

    def _pubsub_close(self):
        """
        Closes the pub/sub object.
        """
        with self._pubsub_lock:
            if self._pubsub is not None:
                try:
                    self._pubsub.close()
                except Exception as e:
                    logger.debug('Error on pubsub close: %s', e)
                finally:
                    self._pubsub = None

    def on_close(self):
        """
        Extensible close handler that closes the pub/sub object.
        """
        self._pubsub_close()

    @staticmethod
    def get_channel(channel: str) -> str:
        """
        Utility method that returns the prefixed Redis channel for a certain subscription name.
        """
        return f'_platypush/{Config.get("device_id")}/{channel}'  # type: ignore


# vim:sw=4:ts=4:et:
