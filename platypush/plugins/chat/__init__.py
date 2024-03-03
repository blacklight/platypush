from platypush.plugins import Plugin, action


class ChatPlugin(Plugin):
    """
    Base class for chat plugins.
    """

    @action
    def send_message(self, *_, **__):
        raise NotImplementedError()
