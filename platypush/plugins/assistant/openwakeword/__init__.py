import os
import pathlib
import queue
import time

from threading import RLock, Thread
from typing import Iterable, List, Optional, Union

from platypush.common.assistant import AudioRecorder
from platypush.config import Config
from platypush.message.event.assistant import HotwordDetectedEvent
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
    :param detection_sensitivity: Wake word detection sensitivity, a float
        between 0.0 and 1.0 (default: 0.5). Higher values increase the
        sensitivity.
    :param frame_duration: Audio frame duration in seconds. Default: 0.5
        seconds.
    :param enable_speex_noise_suppression: Whether to enable Speex-based
        noise suppression (requires the ``speexdsp_ns`` package to be
        installed). By default it's enabled if the package is available.
    :param audio_frame_timeout: Audio frame timeout in seconds. Any frames
        older than this value will be discarded. Default: 5.0 seconds.
    :param pause_seconds_after_hotword: Number of seconds to pause
        detection after a hotword is detected, to prevent multiple
        detections of the same hotword. Default: 2.0 seconds.
    """

    def __init__(
        self,
        models: Optional[Iterable[str]] = None,
        models_directory: Optional[str] = None,
        detection_sensitivity: float = 0.5,
        frame_duration: float = 0.5,
        enable_speex_noise_suppression: Optional[bool] = None,
        audio_frame_timeout: float = 5.0,
        pause_seconds_after_hotword: float = 2.0,
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

        self.detection_sensitivity = detection_sensitivity
        self.frame_duration = frame_duration
        self._pause_seconds_after_hotword = pause_seconds_after_hotword
        self._audio_frame_timeout = audio_frame_timeout
        self._recorder: Optional[AudioRecorder] = None
        self._model = None
        self._audio_lock = RLock()
        self._audio_queue = queue.Queue()
        self._audio_thread: Optional[Thread] = None
        self._last_detection_time = 0.0

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
        assert not missing_models, f"Models not found: {', '.join(missing_models)}"
        return list(models)

    @action
    def list_models(self) -> List[str]:
        """
        List available wake word models.
        """
        from openwakeword import MODELS

        return list(MODELS.keys())

    def _audio_loop(self):
        while not self.should_stop():
            try:
                with AudioRecorder(
                    stop_event=self._should_stop,
                    sample_rate=16000,
                    dtype='int16',
                    frame_size=int(16000 * self.frame_duration),
                    channels=1,
                ) as self._recorder:
                    while not self.should_stop():
                        audio_data = self._recorder.read()
                        if not (audio_data and len(audio_data.data)):
                            continue

                        self._audio_queue.put(audio_data)
            finally:
                if self._recorder:
                    try:
                        self._recorder.stream.close()
                    except Exception as e:
                        self.logger.warning("Error closing the audio stream: %s", e)

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

        assert self._model is not None, "Model not initialized"
        prediction = self._model.predict(audio_data.data)

        if prediction is not None:
            best_match, confidence = None, 0.0
            for model_name, model_confidence in prediction.items():  # type: ignore
                if model_confidence > confidence:
                    best_match = model_name
                    confidence = model_confidence

            if (
                confidence >= self.detection_sensitivity
                and best_match
                and (
                    time.time() - self._last_detection_time
                    >= self._pause_seconds_after_hotword
                )
            ):
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
        super().stop()
        self._stop_audio_thread()
