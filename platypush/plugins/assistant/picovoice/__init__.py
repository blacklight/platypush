from typing import Optional, Sequence

from platypush.plugins import RunnablePlugin, action
from platypush.plugins.assistant import AssistantPlugin

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
        intent_enabled: bool = False,
        keywords: Optional[Sequence[str]] = None,
        keyword_paths: Optional[Sequence[str]] = None,
        keyword_model_path: Optional[str] = None,
        speech_model_path: Optional[str] = None,
        endpoint_duration: Optional[float] = 0.5,
        enable_automatic_punctuation: bool = False,
        start_conversation_on_hotword: bool = True,
        audio_queue_size: int = 100,
        conversation_timeout: Optional[float] = 7.5,
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
        :param intent_enabled: Enable the intent recognition engine (default:
            False).
            **Note**: The intent recognition engine requires you to add Rhino
            to the products available in your Picovoice account.
        :param keywords: List of keywords to listen for (e.g. ``alexa``, ``ok
            google``...). This is required if the wake-word engine is enabled.
            See the `Picovoice repository
            <https://github.com/Picovoice/porcupine/tree/master/resources/keyword_files>`_).
            for a list of the stock keywords available. If you have a custom
            model, you can pass its path to the ``keyword_paths`` parameter and
            its filename (without the path and the platform extension) here.
        :param keyword_paths: List of paths to the keyword files to listen for.
            Custom keyword files can be created using the `Picovoice console
            <https://console.picovoice.ai/ppn>`_ and downloaded from the
            console itself.
        :param keyword_model_path: If you are using a keyword file in a
            non-English language, you can provide the path to the model file
            for its language. Model files are available for all the supported
            languages through the `Picovoice repository
            <https://github.com/Picovoice/porcupine/tree/master/lib/common>`_.
        :param speech_model_path: Path to the speech model file. If you are
            using a language other than English, you can provide the path to the
            model file for that language. Model files are available for all the
            supported languages through the `Picovoice repository
            <https://github.com/Picovoice/porcupine/tree/master/lib/common>`_.
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
        """
        super().__init__(**kwargs)
        self._assistant = None
        self._assistant_args = {
            'stop_event': self._should_stop,
            'access_key': access_key,
            'hotword_enabled': hotword_enabled,
            'stt_enabled': stt_enabled,
            'intent_enabled': intent_enabled,
            'keywords': keywords,
            'keyword_paths': keyword_paths,
            'keyword_model_path': keyword_model_path,
            'speech_model_path': speech_model_path,
            'endpoint_duration': endpoint_duration,
            'enable_automatic_punctuation': enable_automatic_punctuation,
            'start_conversation_on_hotword': start_conversation_on_hotword,
            'audio_queue_size': audio_queue_size,
            'conversation_timeout': conversation_timeout,
            'on_conversation_start': self._on_conversation_start,
            'on_conversation_end': self._on_conversation_end,
            'on_conversation_timeout': self._on_conversation_timeout,
            'on_speech_recognized': self._on_speech_recognized,
            'on_hotword_detected': self._on_hotword_detected,
        }

    @action
    def start_conversation(self, *_, **__):
        """
        Programmatically start a conversation with the assistant
        """
        if not self._assistant:
            self.logger.warning('Assistant not initialized')
            return

        self._assistant.state = AssistantState.DETECTING_SPEECH

    @action
    def stop_conversation(self, *_, **__):
        """
        Programmatically stop a running conversation with the assistant
        """
        if not self._assistant:
            self.logger.warning('Assistant not initialized')
            return

        if self._assistant.hotword_enabled:
            self._assistant.state = AssistantState.DETECTING_HOTWORD
        else:
            self._assistant.state = AssistantState.IDLE

    @action
    def mute(self, *_, **__):
        """
        Mute the microphone. Alias for :meth:`.set_mic_mute` with
        ``muted=True``.
        """

    @action
    def unmute(self, *_, **__):
        """
        Unmute the microphone. Alias for :meth:`.set_mic_mute` with
        ``muted=False``.
        """

    @action
    def set_mic_mute(self, muted: bool):
        """
        Programmatically mute/unmute the microphone.

        :param muted: Set to True or False.
        """

    @action
    def toggle_mute(self, *_, **__):
        """
        Toggle the mic mute state.
        """

    @action
    def send_text_query(self, *_, query: str, **__):
        """
        Send a text query to the assistant.

        This is equivalent to saying something to the assistant.

        :param query: Query to be sent.
        """

    def main(self):
        while not self.should_stop():
            self.logger.info('Starting Picovoice assistant')
            with Assistant(**self._assistant_args) as self._assistant:
                try:
                    for event in self._assistant:
                        self.logger.debug('Picovoice assistant event: %s', event)
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
