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
    def __init__(self, command: str, *args, **kwargs):
        super().__init__(*args, command=command, **kwargs)


# vim:sw=4:ts=4:et:
