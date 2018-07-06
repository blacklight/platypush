"""
.. moduleauthor:: Fabio Manganiello <blacklight86@gmail.com>
"""

from platypush.context import get_backend
from platypush.plugins import Plugin, action

class AssistantGooglePlugin(Plugin):
    """
    Google assistant plugin.
    It acts like a wrapper around the :mod:`platypush.backend.assistant.google`
    backend to programmatically control the conversation status.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @action
    def start_conversation(self):
        """
        Programmatically start a conversation with the assistant
        """
        assistant = get_backend('assistant.google')
        assistant.start_conversation()

    @action
    def stop_conversation(self):
        """
        Programmatically stop a running conversation with the assistant
        """
        assistant = get_backend('assistant.google')
        assistant.stop_conversation()


# vim:sw=4:ts=4:et:

