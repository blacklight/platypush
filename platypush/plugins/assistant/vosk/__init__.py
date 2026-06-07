import json
import os
import time

from threading import Event
from typing import Optional

from platypush.common.assistant import AudioRecorder
from platypush.plugins import RunnablePlugin, action
from platypush.plugins.assistant import AssistantPlugin


# pylint: disable=too-many-ancestors
class AssistantVoskPlugin(AssistantPlugin, RunnablePlugin):
    """
    A voice assistant based on the `Vosk <https://alphacephei.com/vosk/>`_
    offline speech recognition engine.

    Vosk is a lightweight, offline speech recognition toolkit that supports
    multiple languages and runs on various platforms including Raspberry Pi.

    Setup
    -----

    1. Install the plugin dependencies (``pip install vosk sounddevice``).

    2. Download a Vosk model from the `Vosk models page
       <https://alphacephei.com/vosk/models>`_. Small models (~50 MB) are
       available for many languages and provide good accuracy for command
       recognition. Larger models provide better accuracy for free-form
       dictation.

    3. Extract the model to a directory and provide its path via the
       ``model_path`` parameter, or set the ``lang`` parameter to
       auto-download a model for the specified language.

    Hotword detection
    -----------------

    This plugin does not include built-in hotword detection. You can pair it
    with a hotword detection plugin such as
    :class:`platypush.plugins.assistant.picovoice.AssistantPicovoicePlugin`
    (with ``stt_enabled: false``) or
    :class:`platypush.plugins.assistant.openwakeword.AssistantOpenwakewordPlugin`.

    Example configuration with OpenWakeWord for hotword detection:

      .. code-block:: yaml

          assistant.openwakeword:
            models:
              - hey_jarvis

          assistant.vosk:
            model_path: /path/to/vosk-model-en-us-0.22

    Then trigger the conversation on hotword detection:

      .. code-block:: python

          from platypush import run, when
          from platypush.message.event.assistant import HotwordDetectedEvent

          @when(HotwordDetectedEvent)
          def on_hotword_detected():
              run("assistant.vosk.start_conversation")

    Speech recognition
    ------------------

    When a conversation is started (either programmatically via
    :meth:`.start_conversation` or after a hotword is detected), the plugin
    records audio from the microphone and processes it through Vosk in
    real-time. When speech is recognized, a
    :class:`platypush.message.event.assistant.SpeechRecognizedEvent` is fired.

    You can hook into recognized speech:

      .. code-block:: python

          from platypush import when, run
          from platypush.message.event.assistant import SpeechRecognizedEvent

          @when(SpeechRecognizedEvent, phrase='turn on (the)? lights?')
          def on_turn_on_lights(event: SpeechRecognizedEvent, **context):
              run("light.hue.on")

    """

    def __init__(
        self,
        model_path: Optional[str] = None,
        *,
        lang: Optional[str] = None,
        sample_rate: int = 16000,
        frame_size: int = 4000,
        channels: int = 1,
        conversation_start_timeout: float = 5.0,
        conversation_end_timeout: float = 1.5,
        conversation_max_duration: float = 15.0,
        words: bool = False,
        **kwargs,
    ):
        """
        :param model_path: Path to the Vosk model directory. You can download
            models from `<https://alphacephei.com/vosk/models>`_. Either
            ``model_path`` or ``lang`` must be specified.
        :param lang: Language code (e.g. ``en-us``, ``it``, ``de``, ``fr``).
            If specified and ``model_path`` is not set, Vosk will attempt to
            auto-download a small model for this language.
        :param sample_rate: Audio sample rate in Hz (default: 16000). Most
            Vosk models expect 16 kHz audio.
        :param frame_size: Number of samples per audio frame (default: 4000).
            With the default sample rate of 16000, this corresponds to 250 ms
            per frame.
        :param channels: Number of audio channels (default: 1). Vosk requires
            mono audio.
        :param conversation_start_timeout: Seconds to wait for speech after
            starting a conversation before timing out (default: 5.0).
        :param conversation_end_timeout: Seconds of silence after the last
            detected speech before ending the conversation (default: 1.5).
        :param conversation_max_duration: Maximum conversation duration in
            seconds (default: 15.0).
        :param words: If True, include per-word timing and confidence
            information in the recognition results (default: False).
        """
        super().__init__(**kwargs)

        assert model_path or lang, "Either 'model_path' or 'lang' must be specified"

        self._model_path = os.path.expanduser(model_path) if model_path else None
        self._lang = lang
        self._sample_rate = sample_rate
        self._frame_size = frame_size
        self._channels = channels
        self._conversation_start_timeout = conversation_start_timeout
        self._conversation_end_timeout = conversation_end_timeout
        self._conversation_max_duration = conversation_max_duration
        self._words = words
        self._model = None
        self._start_recording_event = Event()
        self._recorder: Optional[AudioRecorder] = None

    def _load_model(self):
        from vosk import Model, SetLogLevel

        SetLogLevel(-1)

        if self._model is not None:
            return

        if self._model_path:
            self.logger.info('Loading Vosk model from: %s', self._model_path)
            self._model = Model(model_path=self._model_path)
        else:
            self.logger.info('Loading Vosk model for language: %s', self._lang)
            self._model = Model(lang=self._lang)

        self.logger.info('Vosk model loaded')

    def _create_recognizer(self):
        from vosk import KaldiRecognizer

        rec = KaldiRecognizer(self._model, self._sample_rate)
        if self._words:
            rec.SetWords(True)
        return rec

    def _wait_recording_start(self):
        while not self.should_stop():
            if self._start_recording_event.wait(timeout=1.0):
                self._start_recording_event.clear()
                return True
        return False

    def _capture_and_recognize(self):
        """
        Record audio and perform streaming recognition using Vosk.
        """
        rec = self._create_recognizer()
        conversation_start = time.time()
        last_speech_time = None
        speech_detected = False
        result = {}

        try:
            with AudioRecorder(
                stop_event=self._should_stop,
                sample_rate=self._sample_rate,
                frame_size=self._frame_size,
                channels=self._channels,
            ) as recorder:
                self._recorder = recorder

                while not self.should_stop() and not recorder.should_stop():
                    elapsed = time.time() - conversation_start

                    # Check max duration
                    if elapsed >= self._conversation_max_duration:
                        self.logger.debug('Conversation max duration reached')
                        break

                    # Check start timeout (no speech detected yet)
                    if (
                        not speech_detected
                        and elapsed >= self._conversation_start_timeout
                    ):
                        self.logger.debug('Conversation start timeout reached')
                        break

                    # Check end timeout (silence after speech)
                    if (
                        speech_detected
                        and last_speech_time
                        and (time.time() - last_speech_time)
                        >= self._conversation_end_timeout
                    ):
                        self.logger.debug('Conversation end timeout (silence) reached')
                        break

                    audio_data = recorder.read(timeout=0.5)
                    if not audio_data or not len(  # pylint: disable=C1802
                        audio_data.data
                    ):
                        continue

                    # Vosk expects bytes (int16 PCM)
                    data = audio_data.data.tobytes()

                    if rec.AcceptWaveform(data):
                        result = json.loads(rec.Result())
                        text = result.get('text', '').strip()
                        if text:
                            speech_detected = True
                            last_speech_time = time.time()
                    else:
                        partial = json.loads(rec.PartialResult())
                        partial_text = partial.get('partial', '').strip()
                        if partial_text:
                            speech_detected = True
                            last_speech_time = time.time()

        finally:
            self._recorder = None

        if not speech_detected:
            return None

        final = json.loads(rec.FinalResult())
        text = final.get('text', '')
        if not text:
            text = result.get('text', '')

        text = text.strip()
        if not text:
            return None

        return text

    def _audio_loop(self):
        while not self.should_stop():
            if not self._wait_recording_start():
                break

            self._on_conversation_start()

            try:
                text = self._capture_and_recognize()
            except Exception as e:
                self.logger.error(
                    'Error during speech recognition: %s', e, exc_info=True
                )
                self._on_conversation_end()
                continue

            if text:
                self._on_speech_recognized(text)
            else:
                self._on_conversation_timeout()

    def _start_conversation(self, *_, **__):
        self._start_recording_event.set()

    def _stop_conversation(self, *_, **__):
        super()._stop_conversation()
        if self._recorder:
            self._recorder.stop()
        self._on_conversation_end()

    @action
    def start_conversation(self, *_, **__):
        """
        Start a conversation with the assistant.

        The conversation will be automatically stopped after
        ``conversation_max_duration`` seconds, or after
        ``conversation_start_timeout`` seconds of silence with no speech
        detected, or after ``conversation_end_timeout`` seconds of silence
        after the last speech, or when :meth:`.stop_conversation` is called.
        """
        self._start_conversation()

    @action
    def mute(self, *_, **__):
        """
        .. note:: This plugin has no continuous hotword detection. Speech
            processing is on-demand via :meth:`.start_conversation` and
            :meth:`.stop_conversation`. Mute/unmute are no-ops.
        """
        self.logger.warning(
            "assistant.vosk.mute is not implemented because this plugin "
            "has no hotword detection"
        )

    @action
    def unmute(self, *_, **__):
        """
        .. note:: This plugin has no continuous hotword detection. Speech
            processing is on-demand via :meth:`.start_conversation` and
            :meth:`.stop_conversation`. Mute/unmute are no-ops.
        """
        self.logger.warning(
            "assistant.vosk.unmute is not implemented because this plugin "
            "has no hotword detection"
        )

    @action
    def send_text_query(self, *_, query: str, **__):
        """
        Send a text query to the assistant (emulates speech recognition).

        :param query: The text query to process.
        """
        self._on_speech_recognized(query)

    def main(self):
        self._load_model()

        while not self.should_stop():
            try:
                self._audio_loop()
            except Exception as e:
                self.logger.error('Audio loop error: %s', e, exc_info=True)
                self.wait_stop(5)

    def stop(self):
        self._stop_conversation()
        super().stop()


# vim:sw=4:ts=4:et:
