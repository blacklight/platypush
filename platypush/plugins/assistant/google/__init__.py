"""
.. moduleauthor:: Fabio Manganiello <blacklight86@gmail.com>
"""

from platypush.context import get_backend
from platypush.plugins import action
from platypush.plugins.assistant import AssistantPlugin


class AssistantGooglePlugin(AssistantPlugin):
    """
    Google assistant plugin.
    It acts like a wrapper around the :mod:`platypush.backend.assistant.google`
    backend to programmatically control the conversation status.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @staticmethod
    def _get_assistant():
        return get_backend('assistant.google')

    @action
    def start_conversation(self):
        """
        Programmatically start a conversation with the assistant
        """
        assistant = self._get_assistant()
        assistant.start_conversation()

    @action
    def stop_conversation(self):
        """
        Programmatically stop a running conversation with the assistant
        """
        assistant = self._get_assistant()
        assistant.stop_conversation()

    @action
    def pause_detection(self):
        assistant = self._get_assistant()
        assistant.pause_detection()

    @action
    def resume_detection(self):
        assistant = self._get_assistant()
        assistant.resume_detection()

    @action
    def is_detecting(self) -> bool:
        assistant = self._get_assistant()
        return assistant.is_detecting()


# vim:sw=4:ts=4:et:
