from abc import ABC, abstractmethod

from platypush.plugins import Plugin

class AssistantPlugin(ABC, Plugin):
    """
    Base class for assistant plugins
    """

    @abstractmethod
    def start_conversation(self, *args, language=None, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def stop_conversation(self, *args, **kwargs):
        raise NotImplementedError


# vim:sw=4:ts=4:et:
