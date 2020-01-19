"""
.. moduleauthor:: Fabio Manganiello <blacklight86@gmail.com>
"""

import os

from platypush.context import get_bus
from platypush.plugins import action
from platypush.plugins.assistant import AssistantPlugin

from platypush.message.event.assistant import ConversationStartEvent, \
    ConversationEndEvent, SpeechRecognizedEvent, ResponseEvent


class AssistantEchoPlugin(AssistantPlugin):
    """
    Amazon Echo/Alexa assistant plugin.

    In order to activate the Echo service on your device follow these steps:

        1. Install avs (``pip install git+https://github.com/BlackLight/avs.git``)
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

    def __init__(self, avs_config_file: str = None, audio_device: str = 'default',
                 audio_player: str = 'default', **kwargs):
        """
        :param avs_config_file: AVS credentials file - default: ~/.avs.json. If the file doesn't exist then
            an instance of the AVS authentication service will be spawned. You can login through an Amazon
            account either in the spawned browser window, if available, or by opening http://your-ip:3000
            in the browser on another machine.

        :param audio_device: Name of the input audio device (default: 'default')
        :param audio_player: Player to be used for audio playback (default: 'default').
            Supported values: 'mpv', 'mpg123', 'gstreamer'
        """
        from avs.alexa import Alexa
        from avs.config import DEFAULT_CONFIG_FILE
        from avs.mic import Audio

        super().__init__(**kwargs)

        if not avs_config_file:
            avs_config_file = DEFAULT_CONFIG_FILE

        if not avs_config_file or not os.path.isfile(avs_config_file):
            from avs.auth import auth
            auth(None, avs_config_file)
            self.logger.warning('Amazon Echo assistant credentials not configured. Open http://localhost:3000 ' +
                                'to authenticate this client')

        self.audio_device = audio_device
        self.audio_player = audio_player
        self.audio = Audio(device_name=audio_device)
        self.alexa = Alexa(avs_config_file, audio_player=audio_player)
        self._ready = False

        self.alexa.state_listener.on_ready = self._on_ready()
        self.alexa.state_listener.on_listening = self._on_listening()
        self.alexa.state_listener.on_speaking = self._on_speaking()
        self.alexa.state_listener.on_thinking = self._on_thinking()
        self.alexa.state_listener.on_finished = self._on_finished()
        self.alexa.state_listener.on_disconnected = self._on_disconnected()

        self.audio.link(self.alexa)
        self.alexa.start()

    def _on_ready(self):
        def _callback():
            self._ready = True
        return _callback

    def _on_listening(self):
        def _callback():
            get_bus().post(ConversationStartEvent(assistant=self))
        return _callback

    def _on_speaking(self):
        def _callback():
            # AVS doesn't provide a way to access the response text
            get_bus().post(ResponseEvent(assistant=self, response_text=''))
        return _callback

    def _on_finished(self):
        def _callback():
            get_bus().post(ConversationEndEvent(assistant=self))
        return _callback

    def _on_disconnected(self):
        def _callback():
            self._ready = False
        return _callback

    def _on_thinking(self):
        def _callback():
            # AVS doesn't provide a way to access the detected text
            get_bus().post(SpeechRecognizedEvent(assistant=self, phrase=''))
        return _callback

    @action
    def start_conversation(self, **kwargs):
        if not self._ready:
            raise RuntimeError('Echo assistant not ready')

        self.audio.start()
        self.alexa.listen()

    @action
    def stop_conversation(self):
        self.audio.stop()
        self._on_finished()()


# vim:sw=4:ts=4:et:
