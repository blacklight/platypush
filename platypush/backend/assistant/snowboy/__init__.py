import json
import os
import subprocess
import time

from snowboy import snowboydecoder

from platypush.backend import Backend
from platypush.message.event.assistant import \
    ConversationStartEvent, ConversationEndEvent, \
    SpeechRecognizedEvent, HotwordDetectedEvent

class AssistantSnowboyBackend(Backend):
    """ Backend for detecting custom voice hotwords through Snowboy.
        The purpose of this component is only to detect the hotword
        specified in your Snowboy voice model. If you want to trigger
        proper assistant conversations or custom speech recognition,
        you should create a hook in your configuration on HotwordDetectedEvent
        to trigger the conversation on whichever assistant plugin you're using
        (Google, Alexa...) """

    def __init__(self, voice_model_file, hotword=None, sensitivity=0.5,
                 audio_gain=1.0, **kwargs):
        """ Params:
            voice_model_file -- Snowboy voice model file
            hotword  -- Name of the hotword
        """

        super().__init__(**kwargs)
        self.voice_model_file = voice_model_file
        self.hotword = hotword
        self.sensitivity = sensitivity
        self.audio_gain = audio_gain

        self.detector = snowboydecoder.HotwordDetector(
            self.voice_model_file, sensitivity=self.sensitivity,
            audio_gain=self.audio_gain)

        self.logger.info('Initialized Snowboy hotword detection')

    def send_message(self, msg):
        pass

    def hotword_detected(self):
        def callback():
            self.bus.post(HotwordDetectedEvent(hotword=self.hotword))
        return callback

    def run(self):
        super().run()
        self.detector.start(self.hotword_detected())


# vim:sw=4:ts=4:et:

