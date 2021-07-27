from platypush.plugins import Plugin, action


class ChatPlugin(Plugin):
    """
    Base class for chat plugins.
    """
    @action
    def send_message(self, *args, **kwargs):
        raise NotImplementedError()
