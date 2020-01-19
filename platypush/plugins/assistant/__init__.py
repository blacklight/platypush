from abc import ABC, abstractmethod

from platypush.plugins import Plugin


class AssistantPlugin(ABC, Plugin):
    """
    Base class for assistant plugins
    """

    @abstractmethod
    def start_conversation(self, *args, language=None, **kwargs):
        """
        Start a conversation.
        """
        raise NotImplementedError

    @abstractmethod
    def stop_conversation(self, *args, **kwargs):
        """
        Stop a conversation.
        """
        raise NotImplementedError

    @abstractmethod
    def pause_detection(self, *args, **kwargs):
        """
        Put the assistant on pause. No new conversation events will be triggered.
        """
        raise NotImplementedError

    @abstractmethod
    def resume_detection(self, *args, **kwargs):
        """
        Resume the assistant hotword detection from a paused state.
        """
        raise NotImplementedError

    @abstractmethod
    def is_detecting(self) -> bool:
        """
        :return: True if the asistant is detecting, False otherwise.
        """
        raise NotImplementedError


# vim:sw=4:ts=4:et:
