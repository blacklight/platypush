from abc import ABCMeta
from datetime import datetime
from typing import Union, Optional, Iterable

from dateutil.tz import gettz

from platypush.message.event import Event


class SlackEvent(Event, ABCMeta):
    """
    Base class for Slack events.
    """
    def __init__(self, *args, timestamp: Optional[Union[int, float, datetime]] = None, **kwargs):
        """
        :param timestamp: Event timestamp.
        """
        kwargs['event_time'] = self._convert_timestamp(timestamp)
        super().__init__(*args, **kwargs)

    @staticmethod
    def _convert_timestamp(timestamp: Optional[Union[int, float, datetime]] = None) -> Optional[datetime]:
        if not (isinstance(timestamp, int) or isinstance(timestamp, float)):
            return timestamp

        return datetime.fromtimestamp(timestamp, tz=gettz())   # lgtm [py/call-to-non-callable]


class SlackMessageEvent(SlackEvent, ABCMeta):  # lgtm [py/conflicting-attributes]
    """
    Base class for message-related events.
    """
    def __init__(self, *args, text: str, user: str, channel: Optional[str] = None, team: Optional[str] = None,
                 icons: dict = None, blocks: Iterable[dict] = None, **kwargs):
        """
        :param text: Message text.
        :param user: ID of the sender.
        :param channel: ID of the channel.
        :param team: ID of the team.
        :param icons: Mapping of the icons for this message.
        :param blocks: Extra blocks in the message.
        """
        super().__init__(*args, text=text, user=user, channel=channel, team=team, icons=icons, blocks=blocks, **kwargs)


class SlackMessageReceivedEvent(SlackMessageEvent):
    """
    Event triggered when a message is received on a monitored resource.
    """


class SlackMessageEditedEvent(SlackMessageEvent):
    """
    Event triggered when a message is edited on a monitored resource.
    """


class SlackMessageDeletedEvent(SlackMessageEvent):
    """
    Event triggered when a message is deleted from a monitored resource.
    """


class SlackAppMentionReceivedEvent(SlackMessageEvent):
    """
    Event triggered when a message that mentions the app is received on a monitored resource.
    """


# vim:sw=4:ts=4:et:
