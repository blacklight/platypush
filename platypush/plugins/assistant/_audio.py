from collections import deque
from logging import getLogger
from typing import Optional

import numpy as np

from platypush.plugins.assistant._vad import SileroVad, get_silero_model_path

# Number of frames to observe before the adaptive noise floor is used to gate the speech detection
NOISE_FLOOR_CALIBRATION_FRAMES = 8
# Adaptation rate of the noise floor when the signal drops below it (fast) or rises above it during non-speech (slow)
NOISE_FLOOR_FALL_RATE = 0.3
NOISE_FLOOR_RISE_RATE = 0.02
# Hysteresis margin: once a frame is speech, its score only needs to reach (threshold - margin)
VAD_HYSTERESIS = 0.15


class AudioPreprocessor:
    """
    Reusable audio preprocessing for assistant plugins.

    Provides three optional processing stages:

    1. **Noise suppression** via `speexdsp_ns
       <https://pypi.org/project/speexdsp-ns/>`_ (Speex DSP).  Auto-enabled
       when the package is installed unless explicitly disabled.

    2. **Voice activity detection (VAD)** for accurate speech / silence
       boundary detection. Uses the `Silero VAD
       <https://github.com/snakers4/silero-vad>`_ neural model (through
       ``onnxruntime``) when available, otherwise `webrtcvad
       <https://pypi.org/project/webrtcvad/>`_, otherwise a simple energy-based
       (RMS) check. The raw per-frame decisions are smoothed with a hysteresis
       threshold and a sliding-window majority vote, so that isolated noise
       bursts don't keep a conversation alive.

    3. **Adaptive noise floor**: the background noise level is tracked over
       time, and frames that are not louder than ``noise_floor_factor`` times
       the noise floor are never considered as speech.

    Usage::

        proc = AudioPreprocessor(
            frame_size=2000,
            sample_rate=16000,
        )

        # In the audio loop:
        data = proc.process(raw_bytes)       # noise-suppressed bytes
        if proc.has_speech(data):
            last_speech_time = time.time()
    """

    def __init__(
        self,
        frame_size: int,
        sample_rate: int,
        *,
        enable_noise_suppression: Optional[bool] = None,
        vad_enabled: bool = True,
        vad_backend: str = 'auto',
        vad_model_path: Optional[str] = None,
        vad_mode: int = 2,
        vad_speech_threshold: float = 0.5,
        vad_window_duration: float = 0.5,
        energy_vad_threshold: float = 300,
        noise_floor_factor: float = 2.0,
    ):
        """
        :param frame_size: Number of int16 samples per audio frame.
        :param sample_rate: Audio sample rate in Hz (e.g. 16000).
        :param enable_noise_suppression: Enable Speex noise suppression.
            ``None`` (default) auto-enables if ``speexdsp_ns`` is installed.
        :param vad_enabled: Enable voice activity detection (default: True).
        :param vad_backend: VAD backend: ``auto`` (Silero if ``onnxruntime``
            is available, then WebRTC, then energy), ``silero``, ``webrtc`` or
            ``energy`` (default: ``auto``).
        :param vad_model_path: Path to the Silero VAD ONNX model. If not set,
            the official v4.0 model is downloaded into the platypush workdir on
            first use.
        :param vad_mode: WebRTC VAD aggressiveness, 0–3 (default: 2). Only used
            by the WebRTC backend.
        :param vad_speech_threshold: Score (0-1) above which a frame is
            considered as speech (default: 0.5). For Silero it's the speech
            probability; for WebRTC it's the fraction of 30 ms sub-frames
            classified as speech.
        :param vad_window_duration: Duration in seconds of the sliding window
            over which the per-frame speech decisions are smoothed by majority
            vote (default: 0.5).
        :param energy_vad_threshold: RMS threshold for the energy-based VAD
            backend. Voices at conversational distance typically produce
            RMS > 300 on int16 scale (~-34 dBFS). Default: 300.
        :param noise_floor_factor: A frame is only considered as speech if its
            RMS is at least this many times the adaptive noise floor (default:
            2.0, i.e. about 6 dB above the background noise).
        """
        self.logger = getLogger(__name__)
        self._frame_size = frame_size
        self._sample_rate = sample_rate
        self._vad_enabled = vad_enabled
        self._vad_speech_threshold = vad_speech_threshold
        self._energy_vad_threshold = energy_vad_threshold
        self._noise_floor_factor = noise_floor_factor
        self._noise_suppressor = None
        self._vad_backend: Optional[str] = None
        self._vad: Optional[SileroVad] = None
        self._noise_floor: Optional[float] = None
        self._noise_frames = 0
        self._frame_active = False
        self._speaking = False
        self._window: deque = deque(
            maxlen=max(1, round(vad_window_duration * sample_rate / frame_size))
        )

        self._init_noise_suppression(enable_noise_suppression)
        self._init_vad(vad_backend, vad_mode, vad_model_path)

    # ------------------------------------------------------------------
    # Feature-detection helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _has_speex_ns() -> bool:
        try:
            from speexdsp_ns import NoiseSuppression  # noqa

            return True
        except ImportError:
            return False

    @staticmethod
    def _has_webrtcvad() -> bool:
        try:
            import webrtcvad  # noqa

            return True
        except ImportError:
            return False

    # ------------------------------------------------------------------
    # Initialisation
    # ------------------------------------------------------------------

    def _init_noise_suppression(self, enabled: Optional[bool]):
        if enabled is None:
            enabled = self._has_speex_ns()

        if not enabled:
            return

        if not self._has_speex_ns():
            self.logger.warning(
                'Noise suppression requested but speexdsp_ns is not installed. '
                'Install it with: pip install speexdsp-ns'
            )
            return

        from speexdsp_ns import NoiseSuppression

        self._noise_suppressor = NoiseSuppression.create(
            self._frame_size, self._sample_rate
        )
        self.logger.info('Speex noise suppression enabled')

    def _init_vad(self, backend: str, vad_mode: int, model_path: Optional[str]):
        if not self._vad_enabled:
            return

        if backend not in ('auto', 'silero', 'webrtc', 'energy'):
            raise ValueError(f'Unsupported VAD backend: {backend}')

        if backend in ('auto', 'silero'):
            try:
                self._vad = SileroVad(
                    get_silero_model_path(model_path), self._sample_rate
                )
                self._vad_backend = 'silero'
                self.logger.info('Silero VAD enabled')
                return
            except Exception as e:
                if backend == 'silero':
                    raise
                self.logger.info(
                    'Silero VAD not available (%s), falling back to WebRTC VAD', e
                )

        if backend in ('auto', 'webrtc') and self._has_webrtcvad():
            import webrtcvad

            self._vad = webrtcvad.Vad(vad_mode)
            self._vad_backend = 'webrtc'
            self.logger.info('WebRTC VAD enabled (mode %d)', vad_mode)
        else:
            self._vad_backend = 'energy'
            self.logger.info(
                'Using energy-based speech detection. '
                'For better accuracy: pip install onnxruntime webrtcvad'
            )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def noise_suppression_enabled(self) -> bool:
        """Whether noise suppression is active."""
        return self._noise_suppressor is not None

    def process(self, data: bytes) -> bytes:
        """
        Apply noise suppression to a frame of int16 PCM audio.

        Returns the (possibly processed) bytes unchanged if noise suppression
        is not available.
        """
        if self._noise_suppressor is None:
            return data
        return self._noise_suppressor.process(data)

    def reset(self):
        """
        Reset the speech detection state, e.g. at the start of a new
        conversation. The learned noise floor is preserved.
        """
        self._window.clear()
        self._frame_active = False
        self._speaking = False
        if self._vad_backend == 'silero':
            self._vad.reset()

    def has_speech(self, data: bytes) -> bool:
        """
        Determine whether an audio frame contains speech.

        The raw per-frame decision is computed by the VAD backend, gated by
        the adaptive noise floor and smoothed with hysteresis and a sliding
        window majority vote. Always returns ``True`` when VAD is disabled.
        """
        if not self._vad_enabled:
            return True

        samples = np.frombuffer(data, dtype=np.int16)
        if not len(samples):
            return False

        rms = float(np.sqrt(np.mean(samples.astype(np.float64) ** 2)))
        score = (
            0.0 if self._is_below_noise_floor(rms) else self._vad_score(samples, rms)
        )

        threshold = self._vad_speech_threshold - (
            VAD_HYSTERESIS if self._frame_active else 0.0
        )
        self._frame_active = score > 0 and score >= threshold

        self._update_noise_floor(rms)
        self._window.append(self._frame_active)
        self._speaking = sum(self._window) / self._window.maxlen >= 0.5
        return self._speaking

    # ------------------------------------------------------------------
    # VAD implementations
    # ------------------------------------------------------------------

    def _vad_score(self, samples: np.ndarray, rms: float) -> float:
        if self._vad_backend == 'silero':
            return self._vad.predict(samples)
        if self._vad_backend == 'webrtc':
            return self._webrtcvad_score(samples.tobytes())
        return 1.0 if rms > self._energy_vad_threshold else 0.0

    def _webrtcvad_score(self, data: bytes) -> float:
        """
        Split the frame into 30 ms sub-frames and return the fraction of them
        classified as speech.
        """
        sub_frame_samples = int(self._sample_rate * 30 / 1000)  # 30 ms
        sub_frame_bytes = sub_frame_samples * 2  # int16 = 2 bytes/sample
        num_sub_frames = len(data) // sub_frame_bytes

        if num_sub_frames == 0:
            return 0.0

        speech_count = sum(
            1
            for i in range(num_sub_frames)
            if self._vad.is_speech(
                data[i * sub_frame_bytes : (i + 1) * sub_frame_bytes],
                self._sample_rate,
            )
        )

        return speech_count / num_sub_frames

    # ------------------------------------------------------------------
    # Adaptive noise floor
    # ------------------------------------------------------------------

    def _is_below_noise_floor(self, rms: float) -> bool:
        return (
            self._noise_frames >= NOISE_FLOOR_CALIBRATION_FRAMES
            and rms < self._noise_floor * self._noise_floor_factor
        )

    def _update_noise_floor(self, rms: float):
        self._noise_frames += 1
        if self._noise_floor is None:
            self._noise_floor = rms
        elif rms < self._noise_floor:
            self._noise_floor += NOISE_FLOOR_FALL_RATE * (rms - self._noise_floor)
        elif not self._speaking:
            self._noise_floor += NOISE_FLOOR_RISE_RATE * (rms - self._noise_floor)


# vim:sw=4:ts=4:et:
