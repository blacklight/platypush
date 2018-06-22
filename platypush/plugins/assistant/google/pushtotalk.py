"""
.. moduleauthor:: Fabio Manganiello <blacklight86@gmail.com>
"""

from platypush.context import get_backend
from platypush.message.response import Response

from platypush.plugins import Plugin

class AssistantGooglePushtotalkPlugin(Plugin):
    """
    Plugin for the Google assistant pushtotalk API.  It acts as a wrapper to
    programmatically control a
    :mod:`platypush.backend.assistant.google.pushtotalk` backend.
    """

    def start_conversation(self):
        """
        Programmatically start a conversation with the assistant
        """
        assistant = get_backend('assistant.google.pushtotalk')
        assistant.start_conversation()
        return Response(output='', errors=[])

    def stop_conversation(self):
        """
        Programmatically stop a running conversation with the assistant
        """
        assistant = get_backend('assistant.google.pushtotalk')
        assistant.stop_conversation()
        return Response(output='', errors=[])

# vim:sw=4:ts=4:et:

