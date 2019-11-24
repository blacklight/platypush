"""
.. moduleauthor:: Fabio Manganiello <blacklight86@gmail.com>
"""

import os

from avs.auth import auth
from avs.alexa import Alexa
from avs.config import DEFAULT_CONFIG_FILE
from avs.mic import Audio

from platypush.context import get_bus
from platypush.plugins import action
from platypush.plugins.assistant import AssistantPlugin

from platypush.message.event.assistant import ConversationStartEvent, \
    ConversationEndEvent, SpeechRecognizedEvent, VolumeChangedEvent, \
    ResponseEvent


class AssistantEchoPlugin(AssistantPlugin):
    """
    Amazon Echo/Alexa assistant plugin.

    In order to activate the Echo service on your device follow these steps:

        1. Install avs (``pip install avs``)
        2. Run the ``alexa-auth`` script. A local webservice will start on port 3000
        3. If a browser instance doesn't open automatically then head to http://localhost:3000
        4. Log in to your Amazon account
        5. The required credentials will be stored to ~/.avs.json

    Triggers:

        * :class:`platypush.message.event.assistant.ConversationStartEvent`
            when a new conversation starts
        * :class:`platypush.message.event.assistant.SpeechRecognizedEvent`
            when a new voice command is recognized
        * :class:`platypush.message.event.assistant.ConversationEndEvent`
            when a new conversation ends

    Requires:

        * **avs** (``pip install avs``)
    """

    def __init__(self, avs_config_file=DEFAULT_CONFIG_FILE, **kwargs):
        """
        :param avs_config_file: AVS credentials file - default: ~/.avs.json. If the file doesn't exist then
            an instance of the AVS authentication service will be spawned. You can login through an Amazon
            account either in the spawned browser window, if available, or by opening http://your-ip:3000
            in the browser on another machine.
        """
        super().__init__(**kwargs)

        if not avs_config_file or not os.path.isfile(avs_config_file):
            auth(None, avs_config_file)
            self.logger.warning('Amazon Echo assistant credentials not configured. Open http://localhost:3000 ' +
                                'to authenticate this client')

        self.audio = Audio()
        self.alexa = Alexa(avs_config_file)
        self._ready = False

        self.alexa.state_listener.on_ready = self._on_ready()
        self.alexa.state_listener.on_listening = self._on_listening()
        self.alexa.state_listener.on_speaking = self._on_speaking()
        self.alexa.state_listener.on_finished = self._on_finished()
        self.alexa.state_listener.on_disconnected = self._on_disconnected()

        self.audio.link(self.alexa)
        self.alexa.start()

    def _on_ready(self):
        def _callback():
            self._ready = True
        return _callback

    @staticmethod
    def _on_listening():
        def _callback():
            get_bus().post(ConversationStartEvent())
        return _callback

    @staticmethod
    def _on_speaking():
        def _callback():
            # AVS doesn't provide a way to access the response text
            get_bus().post(ResponseEvent(response_text=''))
        return _callback

    @staticmethod
    def _on_finished():
        def _callback():
            get_bus().post(ConversationEndEvent())
        return _callback

    def _on_disconnected(self):
        def _callback():
            self._ready = False
        return _callback

    @action
    def start_conversation(self):
        """
        Programmatically start a conversation with the assistant
        """
        if not self._ready:
            raise RuntimeError('Echo assistant not ready')

        self.audio.start()
        self.alexa.listen()

    @action
    def stop_conversation(self):
        """
        Programmatically stop a running conversation with the assistant
        """
        self.audio.stop()
        self._on_finished()()


# vim:sw=4:ts=4:et:
