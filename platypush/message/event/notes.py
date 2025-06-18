import datetime
from abc import ABC
from typing import Optional, Union

from dateutil.parser import isoparse

from platypush.common.notes import Note, NoteCollection
from platypush.message.event import Event

DateLike = Optional[Union[float, str, datetime.datetime]]


class BaseNoteEvent(Event, ABC):
    """
    Base class for note events.
    """

    def __init__(
        self,
        *args,
        plugin: str,
        **kwargs,
    ):
        """
        :param plugin: The name of the plugin that triggered the event.
        """
        super().__init__(*args, plugin=plugin, **kwargs)

    def _parse_timestamp(
        self, timestamp: DateLike = None
    ) -> Optional[datetime.datetime]:
        """
        Parse a timestamp string into a datetime object.
        """
        if timestamp is None:
            return None

        if isinstance(timestamp, datetime.datetime):
            return timestamp

        if isinstance(timestamp, (int, float)):
            return datetime.datetime.fromtimestamp(timestamp)

        try:
            return isoparse(timestamp)
        except ValueError:
            return None


class NoteItemEvent(BaseNoteEvent, ABC):
    """
    Base class for note item events.
    """

    def __init__(  # pylint: disable=useless-parent-delegation
        self, *args, note: Note, **kwargs
    ):
        """
        :param note: Format:

            .. schema:: notes.NoteItemSchema

        """
        super().__init__(*args, note=note, **kwargs)


class NoteCollectionEvent(BaseNoteEvent, ABC):
    """
    Base class for note collection events.
    """

    def __init__(  # pylint: disable=useless-parent-delegation
        self, *args, collection: NoteCollection, **kwargs
    ):
        """
        :param collection: Format:

            .. schema:: notes.NoteCollectionSchema

        """
        super().__init__(*args, collection=collection, **kwargs)


class NoteCreatedEvent(NoteItemEvent):
    """
    Event triggered when a note is created
    """


class NoteUpdatedEvent(NoteItemEvent):
    """
    Event triggered when a note is updated.
    """


class NoteDeletedEvent(NoteItemEvent):
    """
    Event triggered when a note is deleted.
    """


class CollectionCreatedEvent(NoteCollectionEvent):
    """
    Event triggered when a note collection is created.
    """


class CollectionUpdatedEvent(NoteCollectionEvent):
    """
    Event triggered when a note collection is updated.
    """


class CollectionDeletedEvent(NoteCollectionEvent):
    """
    Event triggered when a note collection is deleted.
    """


# vim:sw=4:ts=4:et:
