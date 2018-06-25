import json
import os
import subprocess
import time

from platypush.backend import Backend
from platypush.message.event.assistant import \
    ConversationStartEvent, ConversationEndEvent, \
    SpeechRecognizedEvent, HotwordDetectedEvent

class AssistantSnowboyBackend(Backend):
    """
    Backend for detecting custom voice hotwords through Snowboy.  The purpose of
    this component is only to detect the hotword specified in your Snowboy voice
    model. If you want to trigger proper assistant conversations or custom
    speech recognition, you should create a hook in your configuration on
    HotwordDetectedEvent to trigger the conversation on whichever assistant
    plugin you're using (Google, Alexa...)

    Triggers:

        * :class:`platypush.message.event.assistant.HotwordDetectedEvent` whenever the hotword has been detected

    Requires:

        * **snowboy** (``pip install snowboy``)
    """

    def __init__(self, voice_model_file, hotword=None, sensitivity=0.5,
                 audio_gain=1.0, **kwargs):
        """
        :param voice_model_file: Snowboy voice model file - see https://snowboy.kitt.ai/
        :type voice_model_file: str

        :param hotword: Name of the hotword
        :type hotword: str

        :param sensitivity: Hotword recognition sensitivity, between 0 and 1
        :type sensitivity: float

        :param audio_gain: Audio gain, between 0 and 1
        :type audio_gain: float
        """

        from snowboy import snowboydecoder

        super().__init__(**kwargs)
        self.voice_model_file = voice_model_file
        self.hotword = hotword
        self.sensitivity = sensitivity
        self.audio_gain = audio_gain

        self.detector = snowboydecoder.HotwordDetector(
            self.voice_model_file, sensitivity=self.sensitivity,
            audio_gain=self.audio_gain)

        self.logger.info('Initialized Snowboy hotword detection')

    def hotword_detected(self):
        def callback():
            self.bus.post(HotwordDetectedEvent(hotword=self.hotword))
        return callback

    def run(self):
        super().run()
        self.detector.start(self.hotword_detected())


# vim:sw=4:ts=4:et:

