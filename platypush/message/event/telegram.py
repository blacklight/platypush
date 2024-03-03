from typing import List, Optional

from platypush.message.event import Event


class TelegramEvent(Event):
    """
    Base class for all the Telegram events.
    """

    def __init__(self, *args, chat_id: int, **kwargs):
        super().__init__(*args, chat_id=chat_id, **kwargs)


class MessageEvent(TelegramEvent):
    """
    Event triggered when a new message is received by the Telegram bot.
    """

    def __init__(  # pylint: disable=useless-parent-delegation
        self, *args, message: Optional[dict], user: Optional[dict], **kwargs
    ):
        """
        :param message: .. schema:: telegram.TelegramMessageSchema
        :param user: .. schema:: telegram.TelegramUserSchema
        """
        super().__init__(*args, message=message, user=user, **kwargs)


class CommandMessageEvent(MessageEvent):
    """
    Event triggered when a new message is received by the Telegram bot.
    """

    def __init__(  # pylint: disable=useless-parent-delegation
        self, *args, command: str, cmdargs: Optional[List[str]] = None, **kwargs
    ):
        """
        :param command: Command name.
        :param cmdargs: Command arguments.
        """
        super().__init__(*args, command=command, cmdargs=(cmdargs or []), **kwargs)


class TextMessageEvent(MessageEvent):
    """
    Event triggered when a new text message is received by the Telegram bot.
    """


class PhotoMessageEvent(MessageEvent):
    """
    Event triggered when a new photo message is received by the Telegram bot.
    """


class VideoMessageEvent(MessageEvent):
    """
    Event triggered when a new video message is received by the Telegram bot.
    """


class ContactMessageEvent(MessageEvent):
    """
    Event triggered when a new contact message is received by the Telegram bot.
    """


class LocationMessageEvent(MessageEvent):
    """
    Event triggered when a new location message is received by the Telegram bot.
    """


class DocumentMessageEvent(MessageEvent):
    """
    Event triggered when a new document message is received by the Telegram bot.
    """


class GroupChatCreatedEvent(MessageEvent):
    """
    Event triggered when a new group chat is created.
    """


# vim:sw=4:ts=4:et:
