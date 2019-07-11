"""
.. moduleauthor:: Fabio Manganiello <blacklight86@gmail.com>
.. license: MIT
"""

import json
import os
import subprocess
import time

from platypush.backend import Backend
from platypush.context import get_plugin
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

        * :class:`platypush.message.event.assistant.HotwordDetectedEvent` \
            whenever the hotword has been detected

    Requires:

        * **snowboy** (``pip install snowboy``)

    Manual installation for snowboy and its Python bindings if the command above
    fails:

        $ [sudo] apt-get install libatlas-base-dev swig
        $ [sudo] pip install pyaudio
        $ git clone https://github.com/Kitt-AI/snowboy
        $ cd snowboy/swig/Python3
        $ make
        $ cd ../..
        $ python3 setup.py build
        $ [sudo] python setup.py install

    You will also need a voice model for the hotword detection. You can find
    some under the ``resources/models`` directory of the Snowboy repository,
    or train/download other models from https://snowboy.kitt.ai.
    """

    def __init__(self, voice_model_file, hotword=None, sensitivity=0.5,
                 audio_gain=1.0, assistant_plugin=None, **kwargs):
        """
        :param voice_model_file: Snowboy voice model file - \
            see https://snowboy.kitt.ai/
        :type voice_model_file: str

        :param hotword: Name of the hotword
        :type hotword: str

        :param sensitivity: Hotword recognition sensitivity, between 0 and 1.
            Default: 0.5.
        :type sensitivity: float

        :param audio_gain: Audio gain, between 0 and 1
        :type audio_gain: float

        :param assistant_plugin: By default Snowboy fires a
            :class:`platypush.message.event.assistant.HotwordDetectedEvent` event
            whenever the hotword is detected. You can also pass the plugin name of
            a :class:`platypush.plugins.assistant.AssistantPlugin` instance
            (for example ``assistant.google.pushtotalk``). If set, then the
            assistant plugin will be invoked to start a conversation.
        :type assistant_plugin: str
        """

        try:
            import snowboydecoder
        except ImportError:
            import snowboy.snowboydecoder as snowboydecoder

        super().__init__(**kwargs)
        self.voice_model_file = os.path.abspath(os.path.expanduser(voice_model_file))
        self.hotword = hotword
        self.sensitivity = sensitivity
        self.audio_gain = audio_gain
        self.assistant_plugin = assistant_plugin

        self.detector = snowboydecoder.HotwordDetector(
            self.voice_model_file, sensitivity=self.sensitivity,
            audio_gain=self.audio_gain)

        self.logger.info('Initialized Snowboy hotword detection')

    def hotword_detected(self):
        """
        Callback called on hotword detection
        """

        def callback():
            self.bus.post(HotwordDetectedEvent(hotword=self.hotword))

            if self.assistant_plugin:
                # Trigger assistant conversation
                get_plugin(self.assistant_plugin).start_conversation()

        return callback

    def on_stop(self):
        if self.detector:
            self.detector.terminate()
            self.detector = None

    def run(self):
        super().run()
        self.detector.start(self.hotword_detected())


# vim:sw=4:ts=4:et:
