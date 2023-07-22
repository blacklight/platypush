from platypush.backend.assistant.google import AssistantGoogleBackend
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

    def _get_assistant(self) -> AssistantGoogleBackend:
        backend = get_backend('assistant.google')
        assert backend, 'The assistant.google backend is not configured.'
        return backend

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
    def set_mic_mute(self, muted: bool = True):
        """
        Programmatically mute/unmute the microphone.

        :param muted: Set to True or False.
        """
        assistant = self._get_assistant()
        assistant.set_mic_mute(muted)

    @action
    def toggle_mic_mute(self):
        """
        Toggle the mic mute state.
        """
        assistant = self._get_assistant()
        is_muted = assistant.is_muted()
        self.set_mic_mute(muted=not is_muted)

    @action
    def is_muted(self) -> bool:
        """
        :return: True if the microphone is muted, False otherwise.
        """
        assistant = self._get_assistant()
        return assistant.is_muted()

    @action
    def send_text_query(self, query: str):
        """
        Send a text query to the assistant.

        :param query: Query to be sent.
        """
        assistant = self._get_assistant()
        assistant.send_text_query(query)


# vim:sw=4:ts=4:et:
