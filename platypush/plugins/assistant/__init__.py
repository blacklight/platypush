from abc import ABC, abstractmethod

from platypush.context import get_backend
from platypush.plugins import Plugin, action


class AssistantPlugin(ABC, Plugin):
    """
    Base class for assistant plugins
    """

    @abstractmethod
    def start_conversation(self, *args, language=None, tts_plugin=None, tts_args=None, **kwargs):
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

    def _get_assistant(self):
        return get_backend('assistant.snowboy')

    @action
    def pause_detection(self):
        """
        Put the assistant on pause. No new conversation events will be triggered.
        """
        assistant = self._get_assistant()
        assistant.pause_detection()

    @action
    def resume_detection(self):
        """
        Resume the assistant hotword detection from a paused state.
        """
        assistant = self._get_assistant()
        assistant.resume_detection()

    @action
    def is_detecting(self) -> bool:
        """
        :return: True if the asistant is detecting, False otherwise.
        """
        assistant = self._get_assistant()
        return assistant.is_detecting()


# vim:sw=4:ts=4:et:
