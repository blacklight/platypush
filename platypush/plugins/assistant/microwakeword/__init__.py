import os
import queue
import time

from threading import Event, RLock, Thread
from typing import Callable, Dict, Iterable, List, Optional, Union

from platypush.common.assistant import AudioRecorder
from platypush.config import Config
from platypush.context import get_bus
from platypush.message.event.assistant import (
    ConversationEndEvent,
    ConversationStartEvent,
    HotwordDetectedEvent,
)
from platypush.plugins import RunnablePlugin, action


class AssistantMicrowakewordPlugin(RunnablePlugin):
    """
    Hotword detection plugin that uses `microWakeWord
    <https://github.com/kahrendt/microWakeWord>`_ through the `pymicro-wakeword
    <https://github.com/OHF-Voice/pymicro-wakeword>`_ Python bindings.

    The built-in models (``okay_nabu``, ``hey_jarvis``, ``alexa`` and
    ``hey_mycroft``) are the same ones used by ESPHome and Home Assistant
    Voice. Custom models can be used by passing the name (or the path) of a
    microWakeWord JSON manifest located in ``models_directory``.

    :param models: List of wake word models to use (use :meth:`.list_models`
        to see the built-in models). By default all built-in models are used.
    :param models_directory: Directory where custom microWakeWord manifests
        (``<name>.json``, with the ``.tflite`` model next to it) are stored.
        Default: ``<PLATYPUSH_WORKDIR>/microwakeword/models``
    :param detection_threshold: Minimum probability (between 0.0 and 1.0) for
        a hotword to be detected. Default: the ``probability_cutoff`` defined
        in each model's manifest. Mutually exclusive with
        ``detection_sensitivity``.
    :param detection_sensitivity: Alternative to ``detection_threshold``, a
        float between 0.0 and 1.0. Higher values increase the sensitivity,
        i.e. the threshold is ``1.0 - detection_sensitivity``.
    :param frame_duration: Audio frame duration in seconds. Default: 0.08
        seconds (1280 samples).
    :param patience_frames: Number of consecutive model outputs above the
        detection threshold required before a hotword is detected. Models
        already smooth their output over a sliding window, so the default is
        0 (disabled).
    :param audio_frame_timeout: Audio frame timeout in seconds. Any frames
        older than this value will be discarded. Default: 5.0 seconds.
    :param pause_seconds_after_hotword: Number of seconds to pause
        detection after a hotword is detected, to prevent multiple
        detections of the same hotword. Default: 2.0 seconds.
    :param input_device: Audio input device to use for recording. Supported
        formats: PortAudio/sounddevice device index, PortAudio/sounddevice
        device name, or PulseAudio/PipeWire source name (e.g.
        ``alsa_input.usb-...``; requires ``pactl``). Default: system default
        input device.
    :param input_volume: Recording gain, as a percentage. ``100`` means
        unchanged, values below ``100`` attenuate, and values above ``100``
        amplify with clipping. Default: 100.
    """

    def __init__(
        self,
        models: Optional[Iterable[str]] = None,
        models_directory: Optional[str] = None,
        detection_threshold: Optional[float] = None,
        detection_sensitivity: Optional[float] = None,
        frame_duration: float = 0.08,
        patience_frames: int = 0,
        audio_frame_timeout: float = 5.0,
        pause_seconds_after_hotword: float = 2.0,
        input_device: Optional[Union[int, str]] = None,
        input_volume: float = 100,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.models_directory = os.path.expanduser(
            models_directory
            or os.path.join(Config.get_workdir(), "microwakeword", "models")
        )
        self.models = self._validate_models(models)

        if detection_sensitivity is not None and detection_threshold is not None:
            raise ValueError(
                "Set either detection_threshold or detection_sensitivity, not both"
            )

        if detection_sensitivity is not None:
            if not 0 <= detection_sensitivity <= 1:
                raise ValueError(
                    "detection_sensitivity must be a float between 0.0 and 1.0"
                )
            detection_threshold = 1.0 - detection_sensitivity

        if detection_threshold is not None and not 0 <= detection_threshold <= 1:
            raise ValueError("detection_threshold must be a float between 0.0 and 1.0")

        self.detection_threshold = detection_threshold
        self.frame_duration = frame_duration
        self.input_device = input_device
        self.input_volume = input_volume
        self._patience_frames = patience_frames
        self._pause_seconds_after_hotword = pause_seconds_after_hotword
        self._audio_frame_timeout = audio_frame_timeout
        self._recorder: Optional[AudioRecorder] = None
        self._models: Dict[str, object] = {}
        self._features = None
        self._hits: Dict[str, int] = {}
        self._audio_lock = RLock()
        self._audio_queue = queue.Queue()
        self._audio_thread: Optional[Thread] = None
        self._last_detection_time = 0.0
        self._conversation_active = Event()
        self._unregister_handlers: List[Callable[[], None]] = []

    @staticmethod
    def _builtin_models() -> List[str]:
        from pymicro_wakeword import Model

        return [model.value for model in Model]

    def _manifest_path(self, name: str) -> str:
        return os.path.join(
            self.models_directory, name if name.endswith(".json") else f"{name}.json"
        )

    def _validate_models(
        self, models: Optional[Union[str, Iterable[str]]]
    ) -> List[str]:
        builtin = self._builtin_models()
        if not models:
            return builtin
        if isinstance(models, str):
            models = [models]

        models = list(models)
        missing = [
            model
            for model in models
            if model not in builtin and not os.path.isfile(self._manifest_path(model))
        ]
        if missing:
            raise AssertionError(f"Models not found: {', '.join(missing)}")
        return models

    def _load_models(self):
        from pymicro_wakeword import MicroWakeWord, Model

        builtin = self._builtin_models()
        self._models = {
            name: (
                MicroWakeWord.from_builtin(Model(name))
                if name in builtin
                else MicroWakeWord.from_config(self._manifest_path(name))
            )
            for name in self.models
        }

    def _reset_state(self):
        self._hits = {}
        if self._features is not None:
            self._features.reset()
        for model in self._models.values():
            model.reset()  # type: ignore

    @action
    def list_models(self) -> List[str]:
        """
        List the built-in wake word models.
        """
        return self._builtin_models()

    def _on_conversation_start(self, *_):
        """
        Called when any assistant plugin starts a conversation.
        Releases the audio device so the assistant can use it.
        """
        self._conversation_active.set()
        with self._audio_lock:
            if self._recorder:
                self._recorder.stop()

    def _on_conversation_end(self, *_):
        """
        Called when any assistant plugin ends a conversation.
        Allows the audio loop to re-acquire the device.
        """
        self._last_detection_time = time.time()
        self._conversation_active.clear()

    def _audio_loop(self):
        import sounddevice as sd

        while not self.should_stop():
            # Wait if another assistant is using the audio device
            while self._conversation_active.is_set() and not self.should_stop():
                self._should_stop.wait(timeout=0.5)

            if self.should_stop():
                break

            # Models and features are reset by the main thread, which owns them
            self._audio_queue.put(None)

            try:
                with AudioRecorder(
                    stop_event=self._should_stop,
                    sample_rate=16000,
                    dtype="int16",
                    frame_size=int(16000 * self.frame_duration),
                    channels=1,
                    device=self.input_device,
                    volume=self.input_volume,
                    open_retries=1,
                ) as self._recorder:
                    while (
                        not self.should_stop()
                        and not self._conversation_active.is_set()
                    ):
                        audio_data = self._recorder.read(timeout=1.0)
                        if not (audio_data and len(audio_data.data)):
                            continue

                        self._audio_queue.put(audio_data)
            except (sd.PortAudioError, ValueError) as e:
                self.logger.warning(
                    "Audio device unavailable: %s. Retrying in 5s...", e
                )
                self._should_stop.wait(timeout=5)
            finally:
                self._recorder = None

    def _stop_audio_thread(self):
        with self._audio_lock:
            if self._recorder:
                self._recorder.stop()
                self._recorder = None

            if self._audio_thread and self._audio_thread.is_alive():
                self._audio_thread.join(timeout=5)
                self._audio_thread = None

    def _threshold(self, model) -> float:
        if self.detection_threshold is not None:
            return self.detection_threshold
        return model.probability_cutoff  # type: ignore

    def _process_audio_frame(self, audio_data):
        if time.time() - audio_data.timestamp > self._audio_frame_timeout:
            self.logger.debug("Discarding stale audio frame")
            return

        if self._features is None or not self._models:
            raise AssertionError("Models not initialized")

        for features in self._features.process_streaming(audio_data.data.tobytes()):
            for name, model in self._models.items():
                probability = model.process_streaming_prob(features)  # type: ignore
                if probability is None:
                    continue

                if probability >= self._threshold(model):
                    self._hits[name] = self._hits.get(name, 0) + 1
                else:
                    self._hits[name] = 0

                if (
                    self._hits[name] >= max(1, self._patience_frames)
                    and time.time() - self._last_detection_time
                    >= self._pause_seconds_after_hotword
                ):
                    self._hits[name] = 0
                    self._last_detection_time = time.time()
                    self._bus.post(
                        HotwordDetectedEvent(
                            hotword=name, plugin=str(self), confidence=probability
                        )
                    )
                    return

    def main(self):
        from pymicro_wakeword import MicroWakeWordFeatures

        self._load_models()
        self._features = MicroWakeWordFeatures()
        self.logger.info("Loaded microWakeWord models: %s", ", ".join(self._models))

        # Register conversation event handlers so we release the audio device
        # when another assistant plugin needs it.
        bus = get_bus()
        self._unregister_handlers = [
            bus.register_handler(ConversationStartEvent, self._on_conversation_start),
            bus.register_handler(ConversationEndEvent, self._on_conversation_end),
        ]

        while not self.should_stop():
            try:
                with self._audio_lock:
                    if self._audio_thread is None or not self._audio_thread.is_alive():
                        self._audio_thread = Thread(
                            target=self._audio_loop, daemon=True
                        )
                        self._audio_thread.start()

                while not self.should_stop():
                    with self._audio_lock:
                        if (
                            self._audio_thread is None
                            or not self._audio_thread.is_alive()
                        ):
                            break

                    try:
                        audio_data = self._audio_queue.get(timeout=1.0)
                        if audio_data is None:
                            self._reset_state()
                        else:
                            self._process_audio_frame(audio_data)
                    except queue.Empty:
                        continue
            except Exception as e:
                self.logger.error("Audio loop error: %s", e, exc_info=True)
                self.wait_stop(5)
            finally:
                self._stop_audio_thread()

    def stop(self):
        for unregister in self._unregister_handlers:
            unregister()
        self._unregister_handlers = []
        super().stop()
        self._stop_audio_thread()
