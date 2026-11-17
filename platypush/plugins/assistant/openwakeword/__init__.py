import os
import pathlib
import queue
import time

from threading import Event, RLock, Thread
from typing import Callable, Iterable, List, Optional, Union

from platypush.common.assistant import AudioRecorder
from platypush.config import Config
from platypush.context import get_bus
from platypush.message.event.assistant import (
    ConversationEndEvent,
    ConversationStartEvent,
    HotwordDetectedEvent,
)
from platypush.plugins import RunnablePlugin, action


class AssistantOpenwakewordPlugin(RunnablePlugin):
    """
    Hotword detection plugin that uses `OpenWakeWord
    <https://github.com/dscripka/openWakeWord>`_.

    :param models: List of wake word model to use (use :meth:`.list_models`
        to see the available models). By default all available models are used
        (use with caution as this may consume significant resources).
    :param models_directory: Directory where to store wake word models.
        Default: ``<PLATYPUSH_WORKDIR>/openwakeword/models``
    :param detection_threshold: Minimum confidence score (between 0.0 and
        1.0) for a hotword to be detected. Higher values make detection
        stricter, i.e. fewer false positives but more missed hotwords.
        Default: 0.5. Mutually exclusive with ``detection_sensitivity``.
    :param detection_sensitivity: Alternative to ``detection_threshold``, a
        float between 0.0 and 1.0. Higher values increase the sensitivity,
        i.e. the threshold is ``1.0 - detection_sensitivity``.
    :param frame_duration: Audio frame duration in seconds. Default: 0.08
        seconds (1280 samples, the frame size recommended by OpenWakeWord).
        Longer frames only return the highest score over their sub-frames,
        which can miss hotwords.
    :param patience_frames: Number of consecutive frames above the detection
        threshold required before a hotword is detected. Reduces false
        positives at the cost of a slightly longer detection latency. Default:
        2. Set to 0 to disable.
    :param enable_speex_noise_suppression: Whether to enable Speex-based
        noise suppression (requires the ``speexdsp_ns`` package to be
        installed). By default it's enabled if the package is available.
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
        detection_sensitivity: Optional[float] = None,
        frame_duration: float = 0.08,
        enable_speex_noise_suppression: Optional[bool] = None,
        audio_frame_timeout: float = 5.0,
        pause_seconds_after_hotword: float = 2.0,
        input_device: Optional[Union[int, str]] = None,
        input_volume: float = 100,
        detection_threshold: Optional[float] = None,
        patience_frames: int = 2,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.models_directory = os.path.expanduser(
            models_directory
            or os.path.join(Config.get_workdir(), "openwakeword", "models")
        )
        self.models = self._init_models(
            models=models, models_directory=self.models_directory
        )
        self.enable_speex_noise_suppression = (
            enable_speex_noise_suppression
            if enable_speex_noise_suppression is not None
            else self._has_speex_dsp
        )

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

        if detection_threshold is None:
            detection_threshold = 0.5
        if not 0 <= detection_threshold <= 1:
            raise ValueError("detection_threshold must be a float between 0.0 and 1.0")

        self.detection_threshold = detection_threshold
        self.frame_duration = frame_duration
        self.input_device = input_device
        self.input_volume = input_volume
        self._patience_frames = patience_frames
        self._pause_seconds_after_hotword = pause_seconds_after_hotword
        self._audio_frame_timeout = audio_frame_timeout
        self._recorder: Optional[AudioRecorder] = None
        self._model = None
        self._audio_lock = RLock()
        self._audio_queue = queue.Queue()
        self._audio_thread: Optional[Thread] = None
        self._last_detection_time = 0.0
        self._consecutive_hits = 0
        self._conversation_active = Event()
        self._unregister_handlers: List[Callable[[], None]] = []

    @property
    def _has_speex_dsp(self) -> bool:
        try:
            from speexdsp_ns import NoiseSuppression  # noqa

            return True
        except ImportError:
            return False

    def _init_models(
        self, models: Optional[Union[str, Iterable[str]]], models_directory: str
    ) -> List[str]:
        import openwakeword

        for model in openwakeword.MODELS.values():
            # Update model paths to point to the local models directory
            model["model_path"] = os.path.join(
                models_directory, os.path.basename(model["model_path"])
            )

        if not models:
            return []
        if isinstance(models, str):
            models = [models]

        missing_models = [model for model in models if model not in openwakeword.MODELS]
        if missing_models:
            raise AssertionError(f"Models not found: {', '.join(missing_models)}")
        return list(models)

    @action
    def list_models(self) -> List[str]:
        """
        List available wake word models.
        """
        from openwakeword import MODELS

        return list(MODELS.keys())

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

            if self._model:
                self._model.reset()
            self._consecutive_hits = 0

            try:
                with AudioRecorder(
                    stop_event=self._should_stop,
                    sample_rate=16000,
                    dtype='int16',
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
                    'Audio device unavailable: %s. Retrying in 5s...', e
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

    def _process_audio_frame(self, audio_data):
        if time.time() - audio_data.timestamp > self._audio_frame_timeout:
            self.logger.debug("Discarding stale audio frame")
            return

        if self._model is None:
            raise AssertionError("Model not initialized")
        prediction = self._model.predict(audio_data.data)

        if prediction is not None:
            best_match, confidence = None, 0.0
            for model_name, model_confidence in prediction.items():  # type: ignore
                if model_confidence > confidence:
                    best_match = model_name
                    confidence = model_confidence

            self._consecutive_hits = (
                self._consecutive_hits + 1
                if confidence >= self.detection_threshold
                else 0
            )

            if (
                self._consecutive_hits >= max(1, self._patience_frames)
                and best_match
                and (
                    time.time() - self._last_detection_time
                    >= self._pause_seconds_after_hotword
                )
            ):
                self._consecutive_hits = 0
                self._last_detection_time = time.time()
                self._bus.post(
                    HotwordDetectedEvent(
                        hotword=best_match, plugin=str(self), confidence=confidence
                    )
                )

    def main(self):
        from openwakeword import MODELS
        from openwakeword.model import Model
        from openwakeword.utils import download_models

        pathlib.Path(self.models_directory).mkdir(parents=True, exist_ok=True)
        self.logger.debug("Refreshing available models...")
        download_models(target_directory=self.models_directory)

        self._model = Model(
            wakeword_models=self.models,
            enable_speex_noise_suppression=self.enable_speex_noise_suppression,
            base_path=self.models_directory,
        )

        self.logger.info("Refreshed available models: %s", list(MODELS.keys()))

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
