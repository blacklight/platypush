import os
from typing import Optional, Sequence

from platypush.context import get_plugin
from platypush.plugins import RunnablePlugin, action
from platypush.plugins.assistant import AssistantPlugin
from platypush.plugins.tts.picovoice import TtsPicovoicePlugin

from ._assistant import Assistant
from ._state import AssistantState


# pylint: disable=too-many-ancestors
class AssistantPicovoicePlugin(AssistantPlugin, RunnablePlugin):
    """
    A voice assistant that runs on your device, based on the `Picovoice
    <https://picovoice.ai/>`_ engine.

    .. note:: You will need a PicoVoice account and a personal access key to
        use this integration.

    You can get your personal access key by signing up at the `Picovoice
    console <https://console.picovoice.ai/>`_. You may be asked to submit a
    reason for using the service (feel free to mention a personal Platypush
    integration), and you will receive your personal access key.

    You may also be asked to select which products you want to use. The default
    configuration of this plugin requires the following:

        * **Porcupine**: wake-word engine, if you want the device to listen for
          a specific wake word in order to start the assistant.

        * **Cheetah**: speech-to-text engine, if you want your voice
          interactions to be transcribed into free text - either programmatically
          or when triggered by the wake word. Or:

        * **Rhino**: intent recognition engine, if you want to extract *intents*
          out of your voice commands - for instance, the phrase "set the living
          room temperature to 20 degrees" could be mapped to the intent with the
          following parameters: ``intent``: ``set_temperature``, ``room``:
          ``living_room``, ``temperature``: ``20``.

        * **Leopard**: speech-to-text engine aimed at offline transcription of
          audio files rather than real-time transcription.

        * **Orca**: text-to-speech engine, if you want to create your custom
          logic to respond to user's voice commands and render the responses as
          audio.

    """

    def __init__(
        self,
        access_key: str,
        hotword_enabled: bool = True,
        stt_enabled: bool = True,
        keywords: Optional[Sequence[str]] = None,
        keyword_paths: Optional[Sequence[str]] = None,
        keyword_model_path: Optional[str] = None,
        speech_model_path: Optional[str] = None,
        intent_model_path: Optional[str] = None,
        endpoint_duration: Optional[float] = 0.5,
        enable_automatic_punctuation: bool = False,
        start_conversation_on_hotword: bool = True,
        audio_queue_size: int = 100,
        conversation_timeout: Optional[float] = 7.5,
        muted: bool = False,
        **kwargs,
    ):
        """
        :param access_key: Your Picovoice access key. You can get it by signing
            up at the `Picovoice console <https://console.picovoice.ai/>`.
        :param hotword_enabled: Enable the wake-word engine (default: True).
            **Note**: The wake-word engine requires you to add Porcupine to the
            products available in your Picovoice account.
        :param stt_enabled: Enable the speech-to-text engine (default: True).
            **Note**: The speech-to-text engine requires you to add Cheetah to
            the products available in your Picovoice account.
        :param keywords: List of keywords to listen for (e.g. ``alexa``, ``ok
            google``...). This is required if the wake-word engine is enabled.
            See the `Porcupine keywords repository
            <https://github.com/Picovoice/porcupine/tree/master/resources/keyword_files>`_).
            for a list of the stock keywords available. If you have a custom
            model, you can pass its path to the ``keyword_paths`` parameter and
            its filename (without the path and the platform extension) here.
        :param keyword_paths: List of paths to the keyword files to listen for.
            Custom keyword files can be created using the `Porcupine console
            <https://console.picovoice.ai/ppn>`_ and downloaded from the
            console itself.
        :param keyword_model_path: If you are using a keyword file in a
            non-English language, you can provide the path to the model file
            for its language. Model files are available for all the supported
            languages through the `Porcupine lib repository
            <https://github.com/Picovoice/porcupine/tree/master/lib/common>`_.
        :param speech_model_path: Path to the speech model file. If you are
            using a language other than English, you can provide the path to the
            model file for that language. Model files are available for all the
            supported languages through the `Cheetah repository
            <https://github.com/Picovoice/cheetah/tree/master/lib/common>`_.
            You can also use the `Speech console
            <https://console.picovoice.ai/cat>`_
            to train your custom models. You can use a base model and fine-tune
            it by boosting the detection of your own words and phrases and edit
            the phonetic representation of the words you want to detect.
        :param intent_model_path: Path to the Rhino context model. This is
            required if you want to use the intent recognition engine through
            Rhino. The context model is a file that contains a list of intents
            that can be recognized by the engine. An intent is an action or a
            class of actions that the assistant can recognize, and it can
            contain an optional number of slots to model context variables -
            e.g. temperature, lights group, location, device state etc.
            You can create your own context model using the `Rhino console
            <https://console.picovoice.ai/rhn>`_. For example, you can define a
            context file to control smart home devices by defining the
            following slots:

                - ``device_type``: The device to control (e.g. lights, music)
                - ``device_state``: The target state of the device (e.g. on,
                  off)
                - ``location``: The location of the device (e.g. living
                  room, kitchen, bedroom)
                - ``media_type``: The type of media to play (e.g. music, video)
                - ``media_state``: The state of the media (e.g. play, pause,
                  stop)

            You can then define the following intents:

                - ``device_ctrl``: Control a device state. Supported phrases:
                    - "turn ``$device_state:state`` the ``$location:location``
                      ``$device_type:device``"
                    - "turn ``$device_state:state`` the ``$device_type:device``"

                - ``media_ctrl``: Control media state. Supported phrases:
                    - "``$media_state:state`` the ``$media_type:media``"
                    - "``$media_state:state`` the ``$media_type:media`` in the
                      ``$location:location``"

            Then a phrase like "turn on the lights in the living room" would
            trigger a
            :class:`platypush.message.event.assistant.IntentRecognizedEvent` with:

                .. code-block:: json

                  {
                    "intent": "device_ctrl",
                    "slots": {
                      "type": "lights",
                      "state": "on",
                      "location": "living room"
                    }
                  }

            **Note**: The intent recognition engine requires you to add Rhino
            to the products available in your Picovoice account.
        :param endpoint_duration: If set, the assistant will stop listening when
            no speech is detected for the specified duration (in seconds) after
            the end of an utterance.
        :param enable_automatic_punctuation: Enable automatic punctuation
            insertion.
        :param start_conversation_on_hotword: If set to True (default), a speech
            detection session will be started when the hotword is detected. If
            set to False, you may want to start the conversation programmatically
            by calling the :meth:`.start_conversation` method instead, or run any
            custom logic hotword detection logic. This can be particularly useful
            when you want to run the assistant in a push-to-talk mode, or when you
            want different hotwords to trigger conversations with different models
            or languages.
        :param audio_queue_size: Maximum number of audio frames to hold in the
            processing queue. You may want to increase this value if you are
            running this integration on a slow device and/or the logs report
            audio frame drops too often. Keep in mind that increasing this value
            will increase the memory usage of the integration. Also, a higher
            value may result in higher accuracy at the cost of higher latency.
        :param conversation_timeout: Maximum time to wait for some speech to be
            detected after the hotword is detected. If no speech is detected
            within this time, the conversation will time out and the plugin will
            go back into hotword detection mode, if the mode is enabled. Default:
            7.5 seconds.
        :param muted: Set to True to start the assistant in a muted state. You will
            need to call the :meth:`.unmute` method to start the assistant listening
            for commands, or programmatically call the :meth:`.start_conversation`
            to start a conversation.
        """
        super().__init__(**kwargs)
        self._assistant = None
        self._assistant_args = {
            'stop_event': self._should_stop,
            'access_key': access_key,
            'hotword_enabled': hotword_enabled,
            'stt_enabled': stt_enabled,
            'keywords': keywords,
            'keyword_paths': (
                os.path.expanduser(keyword_path)
                for keyword_path in (keyword_paths or [])
            ),
            'keyword_model_path': (
                os.path.expanduser(keyword_model_path) if keyword_model_path else None
            ),
            'speech_model_path': (
                os.path.expanduser(speech_model_path) if speech_model_path else None
            ),
            'intent_model_path': (
                os.path.expanduser(intent_model_path) if intent_model_path else None
            ),
            'endpoint_duration': endpoint_duration,
            'enable_automatic_punctuation': enable_automatic_punctuation,
            'start_conversation_on_hotword': (
                start_conversation_on_hotword
                if (intent_model_path or stt_enabled)
                else False
            ),
            'audio_queue_size': audio_queue_size,
            'conversation_timeout': conversation_timeout,
            'muted': muted,
            'on_conversation_start': self._on_conversation_start,
            'on_conversation_end': self._on_conversation_end,
            'on_conversation_timeout': self._on_conversation_timeout,
            'on_speech_recognized': self._on_speech_recognized,
            'on_intent_matched': self._on_intent_matched,
            'on_hotword_detected': self._on_hotword_detected,
        }

    @property
    def tts(self) -> TtsPicovoicePlugin:
        p = get_plugin('tts.picovoice')
        assert p, 'Picovoice TTS plugin not configured/found'
        return p

    def _get_tts_plugin(self) -> TtsPicovoicePlugin:
        return self.tts

    def _on_response_render_start(self, text: Optional[str]):
        if self._assistant:
            self._assistant.set_responding(True)
        return super()._on_response_render_start(text)

    def _on_response_render_end(self):
        if self._assistant:
            self._assistant.set_responding(False)

        return super()._on_response_render_end()

    @action
    def start_conversation(self, *_, model_file: Optional[str] = None, **__):
        """
        Programmatically start a conversation with the assistant.

        :param model_file: Override the model file to be used to detect speech
            in this conversation. If not set, the configured
            ``speech_model_path`` will be used.
        """
        if not self._assistant:
            self.logger.warning('Assistant not initialized')
            return

        if not model_file:
            model_file = self._assistant_args['speech_model_path']
        if model_file:
            model_file = os.path.expanduser(model_file)

        self._assistant.override_speech_model(model_file)
        self._assistant.state = AssistantState.DETECTING_SPEECH

    @action
    def stop_conversation(self, *_, **__):
        """
        Programmatically stop a running conversation with the assistant
        """
        if not self._assistant:
            self.logger.warning('Assistant not initialized')
            return

        self._assistant.override_speech_model(None)

        if self._assistant.hotword_enabled:
            self._assistant.state = AssistantState.DETECTING_HOTWORD
        else:
            self._assistant.state = AssistantState.IDLE

    @action
    def say(self, text: str, *args, **kwargs):
        """
        Proxy to
        :class:`platypush.plugins.tts.picovoice.TtsPicovoicePlugin.say` to
        render some text as speech through the Picovoice TTS engine.

        Extra arguments to
        :class:`platypush.plugins.tts.picovoice.TtsPicovoicePlugin.say` can be
        passed over ``args`` and ``kwargs``.

        :param text: Text to be rendered as speech.
        """
        return self.tts.say(text, *args, **kwargs)

    @action
    def transcribe(self, audio_file: str, *_, model_file: Optional[str] = None, **__):
        """
        Transcribe an audio file to text using the `Leopard
        <https://picovoice.ai/docs/leopard/>`_ engine.

        :param text: Text to be transcribed.
        :param model_file: Override the model file to be used to detect speech
            in this conversation. If not set, the configured
            ``speech_model_path`` will be used.
        :return: dict

          .. code-block:: json

            {
              "transcription": "This is a test",
              "words": [
                {
                  "word": "this",
                  "start": 0.06400000303983688,
                  "end": 0.19200000166893005,
                  "confidence": 0.9626294374465942
                },
                {
                  "word": "is",
                  "start": 0.2879999876022339,
                  "end": 0.35199999809265137,
                  "confidence": 0.9781675934791565
                },
                {
                  "word": "a",
                  "start": 0.41600000858306885,
                  "end": 0.41600000858306885,
                  "confidence": 0.9764975309371948
                },
                {
                  "word": "test",
                  "start": 0.5120000243186951,
                  "end": 0.8320000171661377,
                  "confidence": 0.9511580467224121
                }
              ]
            }

        """
        import pvleopard

        audio_file = os.path.expanduser(audio_file)
        if not model_file:
            model_file = self._assistant_args['speech_model_path']
        if model_file:
            model_file = os.path.expanduser(model_file)

        leopard = pvleopard.create(
            access_key=self._assistant_args['access_key'], model_path=model_file
        )

        transcript, words = leopard.process_file(audio_file)

        try:
            return {
                'transcription': transcript,
                'words': [
                    {
                        'word': word.word,
                        'start': word.start_sec,
                        'end': word.end_sec,
                        'confidence': word.confidence,
                    }
                    for word in words
                ],
            }
        finally:
            leopard.delete()

    @action
    def mute(self, *_, **__):
        """
        Mute the microphone. Alias for :meth:`.set_mic_mute` with
        ``muted=True``.
        """
        return self.set_mic_mute(muted=True)

    @action
    def unmute(self, *_, **__):
        """
        Unmute the microphone. Alias for :meth:`.set_mic_mute` with
        ``muted=False``.
        """
        return self.set_mic_mute(muted=False)

    @action
    def set_mic_mute(self, muted: bool):
        """
        Programmatically mute/unmute the microphone.

        :param muted: Set to True or False.
        """
        if self._assistant:
            self._assistant.set_mic_mute(muted)

        super()._on_mute_changed(muted)

    @action
    def toggle_mute(self, *_, **__):
        """
        Toggle the mic mute state.
        """
        return self.set_mic_mute(not self._is_muted)

    @action
    def send_text_query(self, *_, query: str, **__):
        """
        Send a text query to the assistant.

        This is equivalent to saying something to the assistant.

        :param query: Query to be sent.
        """
        self._on_speech_recognized(query)

    def main(self):
        while not self.should_stop():
            self.logger.info('Starting Picovoice assistant')
            with Assistant(**self._assistant_args) as self._assistant:
                try:
                    for event in self._assistant:
                        if event is not None:
                            self.logger.debug('Dequeued assistant event: %s', event)
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    self.logger.error('Picovoice assistant error: %s', e, exc_info=True)
                    self.wait_stop(5)

    def stop(self):
        try:
            self.stop_conversation()
        except RuntimeError:
            pass

        super().stop()


# vim:sw=4:ts=4:et:
