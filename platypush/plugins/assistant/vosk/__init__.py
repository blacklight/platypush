import hashlib
import json
import os
import pathlib
import time
import urllib.request
import zipfile

from threading import Event
from typing import Optional, Union

from platypush.common.assistant import AudioRecorder
from platypush.config import Config
from platypush.plugins import RunnablePlugin, action
from platypush.plugins.assistant import AssistantPlugin
from platypush.plugins.assistant._audio import AudioPreprocessor

_VOSK_MODEL_LIST_URL = 'https://alphacephei.com/vosk/models/model-list.json'


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

    2. Either set the ``lang`` parameter (e.g. ``en``, ``en-us``, ``it``,
       ``de``) and the plugin will automatically download the best matching
       small model, or manually download a Vosk model from the `Vosk models
       page <https://alphacephei.com/vosk/models>`_ and provide its path via
       ``model_path``.

    Models are stored by default under
    ``<PLATYPUSH_WORKDIR>/assistant.vosk/models``.

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
            lang: en  # auto-downloads a small en-us model
            # or: model_path: /path/to/vosk-model-en-us-0.22

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
        models_directory: Optional[str] = None,
        sample_rate: int = 16000,
        frame_size: int = 2000,
        channels: int = 1,
        input_device: Optional[Union[int, str]] = None,
        input_volume: float = 100,
        conversation_start_timeout: float = 5.0,
        conversation_end_timeout: float = 1.5,
        conversation_max_duration: float = 15.0,
        words: bool = False,
        enable_noise_suppression: Optional[bool] = None,
        vad_enabled: bool = True,
        vad_mode: int = 2,
        vad_speech_threshold: float = 0.3,
        energy_vad_threshold: float = 300,
        **kwargs,
    ):
        """
        :param model_path: Path to the Vosk model directory. You can download
            models from `<https://alphacephei.com/vosk/models>`_. Either
            ``model_path`` or ``lang`` must be specified.
        :param lang: Language code (e.g. ``en``, ``en-us``, ``it``, ``de``,
            ``fr``). If specified and ``model_path`` is not set, the plugin
            will automatically download the best matching small model from
            the Vosk model repository. Generic codes like ``en`` will match
            the most common regional variant (e.g. ``en-us``).
        :param models_directory: Directory where downloaded models are stored.
            Default: ``<PLATYPUSH_WORKDIR>/assistant.vosk/models``.
        :param sample_rate: Audio sample rate in Hz (default: 16000). Most
            Vosk models expect 16 kHz audio.
        :param frame_size: Number of samples per audio frame (default: 2000).
            With the default sample rate of 16000, this corresponds to 125 ms
            per frame. Smaller values reduce latency but increase CPU usage.
        :param channels: Number of audio channels (default: 1). Vosk requires
            mono audio.
        :param input_device: Audio input device to use for recording. Supported
            formats: PortAudio/sounddevice device index, PortAudio/sounddevice
            device name, or PulseAudio/PipeWire source name (e.g.
            ``alsa_input.usb-...``; requires ``pactl``). Default: system
            default input device.
        :param input_volume: Recording gain, as a percentage. ``100`` means
            unchanged, values below ``100`` attenuate, and values above ``100``
            amplify with clipping. Default: 100.
        :param conversation_start_timeout: Seconds to wait for speech after
            starting a conversation before timing out (default: 5.0).
        :param conversation_end_timeout: Seconds of silence after the last
            detected speech before ending the conversation (default: 1.5).
        :param conversation_max_duration: Maximum conversation duration in
            seconds (default: 15.0).
        :param words: If True, include per-word timing and confidence
            information in the recognition results (default: False).
        :param enable_noise_suppression: Whether to enable Speex-based noise
            suppression (requires the ``speexdsp_ns`` package). Reduces
            background noise and improves recognition, especially for distant
            speech. Default: auto-enabled if the package is available.
        :param vad_enabled: Whether to use Voice Activity Detection for
            speech boundary detection (default: True). Uses ``webrtcvad`` if
            available, otherwise falls back to energy-based detection. VAD
            enables faster end-of-speech detection (~300 ms vs. relying on
            Vosk partial result timeouts).
        :param vad_mode: WebRTC VAD aggressiveness mode, 0–3 (default: 2).
            Higher values are more aggressive at filtering non-speech but
            may miss distant or quiet speech.  Only used when ``webrtcvad``
            is installed.
        :param vad_speech_threshold: Fraction of VAD sub-frames within an
            audio frame that must be classified as speech for the frame to
            be considered as containing speech (default: 0.3).
        :param energy_vad_threshold: RMS energy threshold for the
            energy-based VAD fallback (used when ``webrtcvad`` is not
            installed).  Voices at conversational distance typically
            produce RMS > 300 on int16 scale (~-34 dBFS).  Lower values
            improve sensitivity for distant or quiet speech at the cost
            of more false positives.  Default: 300.
        """
        super().__init__(**kwargs)

        if not (model_path or lang):
            raise AssertionError("Either 'model_path' or 'lang' must be specified")

        self._model_path = os.path.expanduser(model_path) if model_path else None
        self._lang = lang
        self._models_directory = os.path.expanduser(
            models_directory
            or os.path.join(Config.get_workdir(), 'assistant.vosk', 'models')
        )
        self._sample_rate = sample_rate
        self._frame_size = frame_size
        self._channels = channels
        self._input_device = input_device
        self._input_volume = input_volume
        self._conversation_start_timeout = conversation_start_timeout
        self._conversation_end_timeout = conversation_end_timeout
        self._conversation_max_duration = conversation_max_duration
        self._words = words
        self._enable_noise_suppression = enable_noise_suppression
        self._vad_enabled = vad_enabled
        self._vad_mode = vad_mode
        self._vad_speech_threshold = vad_speech_threshold
        self._energy_vad_threshold = energy_vad_threshold
        self._model = None
        self._audio_processor: Optional[AudioPreprocessor] = None
        self._start_recording_event = Event()
        self._recorder: Optional[AudioRecorder] = None

    def _resolve_model_path(self) -> str:
        """
        Resolve the model path: if ``model_path`` is set, use it directly;
        otherwise fetch the Vosk model list and download the best matching
        small model for the configured language.
        """
        if self._model_path:
            return self._model_path

        if not (self._lang):
            raise AssertionError("Either 'model_path' or 'lang' must be specified")
        lang = self._lang.lower().strip()

        # Check if a model for this language is already downloaded
        existing = self._find_local_model(lang)
        if existing:
            self.logger.info(
                'Using existing Vosk model: %s', os.path.basename(existing)
            )
            return existing

        self.logger.info(
            'Fetching Vosk model list to find a model for language: %s', lang
        )

        model_list = self._fetch_model_list()
        best = self._pick_best_model(lang, model_list)

        if not (best):
            raise AssertionError(
                f"No Vosk model found for language '{lang}'. "
                f"Check available languages at {_VOSK_MODEL_LIST_URL}"
            )

        return self._download_model(best)

    def _fetch_model_list(self) -> list:
        """Fetch the model list JSON from the Vosk website."""
        with urllib.request.urlopen(_VOSK_MODEL_LIST_URL, timeout=30) as resp:
            return json.loads(resp.read().decode('utf-8'))

    def _pick_best_model(self, lang: str, model_list: list) -> Optional[dict]:
        """
        Find the best matching model for the given language code.

        Matching rules (in priority order):

        1. Exact match on the ``lang`` field.
        2. Prefix match: e.g. ``en`` matches ``en-us``, ``en-in``, ``en-gb``.

        Among matches, non-obsolete models are preferred. Then "small" models
        are preferred over "big" ones, and among models of the same type the
        smallest by download size is chosen.
        """
        exact = [m for m in model_list if m.get('lang', '').lower() == lang]
        prefix = [
            m for m in model_list if m.get('lang', '').lower().startswith(lang + '-')
        ]

        candidates = exact or prefix
        if not candidates:
            return None

        # Filter out obsolete models if there are non-obsolete alternatives
        non_obsolete = [m for m in candidates if m.get('obsolete') != 'true']
        if non_obsolete:
            candidates = non_obsolete

        # Prefer small models
        small = [m for m in candidates if m.get('type') == 'small']
        if small:
            candidates = small

        # Pick the smallest by size
        candidates.sort(key=lambda m: m.get('size', float('inf')))
        return candidates[0]

    def _find_local_model(self, lang: str) -> Optional[str]:
        """
        Look for an already-downloaded model matching the language in the
        models directory.
        """
        if not os.path.isdir(self._models_directory):
            return None

        # Prefer small models; sort alphabetically so the latest version wins
        matches = []
        for entry in sorted(os.listdir(self._models_directory)):
            entry_lower = entry.lower()
            if not entry_lower.startswith('vosk-model'):
                continue

            # Check language match: exact (e.g. vosk-model-small-fr-0.22)
            # or prefix (e.g. vosk-model-small-en-us-0.15 for lang="en")
            # Strip the "vosk-model-" or "vosk-model-small-" prefix to get
            # the lang+version portion.
            rest = entry_lower.removeprefix('vosk-model-')
            is_small = rest.startswith('small-')
            if is_small:
                rest = rest.removeprefix('small-')

            if rest == lang or rest.startswith(lang + '-'):
                full_path = os.path.join(self._models_directory, entry)
                if os.path.isdir(full_path):
                    matches.append((is_small, entry, full_path))

        if not matches:
            return None

        # Prefer small models, then latest by name
        matches.sort(key=lambda m: (m[0], m[1]), reverse=True)
        return matches[0][2]

    def _download_model(self, model_info: dict) -> str:
        """
        Download and extract a Vosk model zip into the models directory.
        Returns the path to the extracted model directory.
        """
        name = model_info['name']
        url = model_info['url']
        expected_md5 = model_info.get('md5')
        dest_dir = os.path.join(self._models_directory, name)

        if os.path.isdir(dest_dir):
            self.logger.info('Model %s already exists at %s', name, dest_dir)
            return dest_dir

        pathlib.Path(self._models_directory).mkdir(parents=True, exist_ok=True)
        zip_path = os.path.join(self._models_directory, f'{name}.zip')

        self.logger.info(
            'Downloading Vosk model %s (%s) ...',
            name,
            model_info.get('size_text', 'unknown size'),
        )

        try:
            urllib.request.urlretrieve(url, zip_path)

            if expected_md5:
                actual_md5 = self._md5(zip_path)
                if not (actual_md5 == expected_md5):
                    raise AssertionError(
                        f'MD5 mismatch for {name}: '
                        f'expected {expected_md5}, got {actual_md5}'
                    )

            self.logger.info('Extracting %s ...', name)
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(self._models_directory)

            if not (os.path.isdir(dest_dir)):
                raise AssertionError(
                    f'Expected model directory {dest_dir} not found after extraction'
                )
        finally:
            if os.path.isfile(zip_path):
                os.remove(zip_path)

        self.logger.info('Vosk model %s ready at %s', name, dest_dir)
        return dest_dir

    @staticmethod
    def _md5(path: str) -> str:
        """Compute MD5 hex digest of a file."""
        h = hashlib.md5()
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(1 << 20), b''):
                h.update(chunk)
        return h.hexdigest()

    def _load_model(self):
        from vosk import Model, SetLogLevel

        SetLogLevel(-1)

        if self._model is not None:
            return

        model_path = self._resolve_model_path()
        self.logger.info('Loading Vosk model from: %s', model_path)
        self._model = Model(model_path=model_path)
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

        Audio pipeline:
        1. Read raw audio frame from microphone
        2. Apply noise suppression (if enabled)
        3. Detect speech via VAD (if enabled)
        4. Feed (always) to Vosk for recognition
        5. Use VAD result for speech boundary timing
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
                device=self._input_device,
                volume=self._input_volume,
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

                    audio_data = recorder.read(timeout=0.25)
                    if not audio_data or not len(  # pylint: disable=C1802
                        audio_data.data
                    ):
                        continue

                    # Vosk expects bytes (int16 PCM)
                    data = audio_data.data.tobytes()

                    # Audio preprocessing:
                    # - VAD runs on the ORIGINAL audio (before NS) so that
                    #   weak distant speech is not suppressed before detection
                    # - NS is applied only to what Vosk receives
                    if self._audio_processor is not None:
                        frame_is_speech = self._audio_processor.has_speech(data)
                        data = self._audio_processor.process(data)
                        if frame_is_speech:
                            speech_detected = True
                            last_speech_time = time.time()

                    # Always feed audio to Vosk (it needs continuous stream)
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
        self._audio_processor = AudioPreprocessor(
            frame_size=self._frame_size,
            sample_rate=self._sample_rate,
            enable_noise_suppression=self._enable_noise_suppression,
            vad_enabled=self._vad_enabled,
            vad_mode=self._vad_mode,
            vad_speech_threshold=self._vad_speech_threshold,
            energy_vad_threshold=self._energy_vad_threshold,
        )

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
