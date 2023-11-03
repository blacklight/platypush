from abc import ABC, abstractmethod

from . import EntityManager


class AssistantEntityManager(EntityManager, ABC):
    """
    Base class for voice assistant integrations that support entity management.
    """

    @abstractmethod
    def start_conversation(self, *args, **kwargs):
        """
        Programmatically starts a conversation.
        """
        raise NotImplementedError()

    @abstractmethod
    def stop_conversation(self, *args, **kwargs):
        """
        Programmatically stops a conversation.
        """
        raise NotImplementedError()

    @abstractmethod
    def is_muted(self, *args, **kwargs) -> bool:
        """
        :return: True if the microphone is muted, False otherwise.
        """
        raise NotImplementedError()

    @abstractmethod
    def mute(self, *args, **kwargs):
        """
        Mute the microphone.
        """
        raise NotImplementedError()

    @abstractmethod
    def unmute(self, *args, **kwargs):
        """
        Unmute the microphone.
        """
        raise NotImplementedError()

    def toggle_mute(self, *_, **__):
        """
        Toggle the mute state of the microphone.
        """
        return self.mute() if self.is_muted() else self.unmute()

    @abstractmethod
    def pause_detection(self, *args, **kwargs):
        """
        Put the assistant on pause. No new conversation events will be triggered.
        """
        raise NotImplementedError()

    @abstractmethod
    def resume_detection(self, *args, **kwargs):
        """
        Resume the assistant hotword detection from a paused state.
        """
        raise NotImplementedError()

    @abstractmethod
    def is_detecting(self, *args, **kwargs) -> bool:
        """
        :return: True if the asistant is detecting, False otherwise.
        """
        raise NotImplementedError()

    @abstractmethod
    def send_text_query(self, *args, **kwargs):
        """
        Send a text query to the assistant.
        """
        raise NotImplementedError()
