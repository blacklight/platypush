"""
.. moduleauthor:: Fabio Manganiello <blacklight86@gmail.com>
.. license: MIT
"""

import os
import threading

from platypush.backend.assistant import AssistantBackend
from platypush.context import get_plugin
from platypush.message.event.assistant import HotwordDetectedEvent


class AssistantSnowboyBackend(AssistantBackend):
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

    Manual installation for snowboy and its Python bindings if the command above fails::

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

    def __init__(self, models, audio_gain=1.0, **kwargs):
        """
        :param models: Map (name -> configuration) of voice models to be used by
            the assistant.  See https://snowboy.kitt.ai/ for training/downloading
            models. Sample format::

                ok_google:    # Hotword model name
                    voice_model_file: /path/models/OK Google.pmdl  # Voice model file location
                    sensitivity: 0.5            # Model sensitivity, between 0 and 1 (default: 0.5)
                    assistant_plugin: assistant.google.pushtotalk  # When the hotword is detected trigger the Google
                                                                   # push-to-talk assistant plugin (optional)
                    assistant_language: en-US   # The assistant will conversate in English when this hotword is
                        detected (optional)
                    detect_sound: /path/to/bell.wav   # Sound file to be played when the hotword is detected (optional)

                ciao_google:  # Hotword model name
                    voice_model_file: /path/models/Ciao Google.pmdl  # Voice model file location
                    sensitivity: 0.5            # Model sensitivity, between 0 and 1 (default: 0.5)
                    assistant_plugin: assistant.google.pushtotalk    # When the hotword is detected trigger the Google
                                                                     # push-to-talk assistant plugin (optional)
                    assistant_language: it-IT   # The assistant will conversate in Italian when this hotword is
                                                # detected (optional)
                    detect_sound: /path/to/bell.wav   # Sound file to be played when the hotword is detected (optional)

        :type models: dict

        :param audio_gain: Audio gain, between 0 and 1. Default: 1
        :type audio_gain: float
        """

        try:
            import snowboydecoder
        except ImportError:
            import snowboy.snowboydecoder as snowboydecoder

        super().__init__(**kwargs)

        self.models = {}
        self._init_models(models)
        self.audio_gain = audio_gain

        self.detector = snowboydecoder.HotwordDetector(
            [model['voice_model_file'] for model in self.models.values()],
            sensitivity=[model['sensitivity'] for model in self.models.values()],
            audio_gain=self.audio_gain)

        self.logger.info('Initialized Snowboy hotword detection with {} voice model configurations'.
                         format(len(self.models)))

    def _init_models(self, models):
        if not models:
            raise AttributeError('Please specify at least one voice model')

        self.models = {}
        for name, conf in models.items():
            if name in self.models:
                raise AttributeError('Duplicate model key {}'.format(name))

            model_file = conf.get('voice_model_file')
            detect_sound = conf.get('detect_sound')

            if not model_file:
                raise AttributeError('No voice_model_file specified for model {}'.format(name))

            model_file = os.path.abspath(os.path.expanduser(model_file))
            assistant_plugin_name = conf.get('assistant_plugin')

            if detect_sound:
                detect_sound = os.path.abspath(os.path.expanduser(detect_sound))

            if not os.path.isfile(model_file):
                raise FileNotFoundError('Voice model file {} does not exist or it not a regular file'.
                                        format(model_file))

            self.models[name] = {
                'voice_model_file': model_file,
                'sensitivity': conf.get('sensitivity', 0.5),
                'detect_sound': detect_sound,
                'assistant_plugin': get_plugin(assistant_plugin_name) if assistant_plugin_name else None,
                'assistant_language': conf.get('assistant_language'),
                'tts_plugin': conf.get('tts_plugin'),
                'tts_args': conf.get('tts_args', {}),
            }

    def hotword_detected(self, hotword):
        """
        Callback called on hotword detection
        """
        try:
            import snowboydecoder
        except ImportError:
            import snowboy.snowboydecoder as snowboydecoder

        def sound_thread(sound):
            snowboydecoder.play_audio_file(sound)

        def callback():
            if not self.is_detecting():
                self.logger.info('Hotword detected but assistant response currently paused')
                return

            self.bus.post(HotwordDetectedEvent(hotword=hotword))
            model = self.models[hotword]

            detect_sound = model.get('detect_sound')
            assistant_plugin = model.get('assistant_plugin')
            assistant_language = model.get('assistant_language')
            tts_plugin = model.get('tts_plugin')
            tts_args = model.get('tts_args')

            if detect_sound:
                threading.Thread(target=sound_thread, args=(detect_sound,)).start()

            if assistant_plugin:
                assistant_plugin.start_conversation(language=assistant_language, tts_plugin=tts_plugin,
                                                    tts_args=tts_args)

        return callback

    def on_stop(self):
        super().on_stop()
        if self.detector:
            self.detector.terminate()
            self.detector = None

    def run(self):
        super().run()
        self.detector.start(detected_callback=[
            self.hotword_detected(hotword)
            for hotword in self.models.keys()
        ])


# vim:sw=4:ts=4:et:
