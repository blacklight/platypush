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

    def _get_assistant(self):
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


# vim:sw=4:ts=4:et:
