from typing import List, Optional

from platypush.message.event import Event


class TelegramEvent(Event):
    def __init__(self, *args, chat_id: int, **kwargs):
        super().__init__(*args, chat_id=chat_id, **kwargs)


class MessageEvent(TelegramEvent):
    """
    Event triggered when a new message is received by the Telegram bot.
    """
    def __init__(self, *args, message, user, **kwargs):
        super().__init__(*args, message=message, user=user, **kwargs)


class CommandMessageEvent(MessageEvent):
    """
    Event triggered when a new message is received by the Telegram bot.
    """
    def __init__(self, command: str, cmdargs: Optional[List[str]] = None, *args, **kwargs):
        super().__init__(*args, command=command, cmdargs=(cmdargs or []), **kwargs)


class TextMessageEvent(MessageEvent):
    pass


class PhotoMessageEvent(MessageEvent):
    pass


class VideoMessageEvent(MessageEvent):
    pass


class ContactMessageEvent(MessageEvent):
    pass


class LocationMessageEvent(MessageEvent):
    pass


class DocumentMessageEvent(MessageEvent):
    pass


class GroupChatCreatedEvent(MessageEvent):
    pass


# vim:sw=4:ts=4:et:
