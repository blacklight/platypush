from platypush.context import get_backend
from platypush.message.response import Response

from platypush.plugins import Plugin

class AssistantGooglePlugin(Plugin):
    def start_conversation(self):
        assistant = get_backend('assistant.google')
        assistant.start_conversation()
        return Response(output='', errors=[])

    def stop_conversation(self):
        assistant = get_backend('assistant.google')
        assistant.stop_conversation()
        return Response(output='', errors=[])

# vim:sw=4:ts=4:et:

