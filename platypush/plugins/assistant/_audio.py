from logging import getLogger
from typing import Optional

import numpy as np


class AudioPreprocessor:
    """
    Reusable audio preprocessing for assistant plugins.

    Provides two optional processing stages:

    1. **Noise suppression** via `speexdsp_ns
       <https://pypi.org/project/speexdsp-ns/>`_ (Speex DSP).  Auto-enabled
       when the package is installed unless explicitly disabled.

    2. **Voice activity detection (VAD)** for accurate speech / silence
       boundary detection.  Uses `webrtcvad
       <https://pypi.org/project/webrtcvad/>`_ when available, otherwise
       falls back to a simple energy-based (RMS) check.

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
        vad_mode: int = 2,
        vad_speech_threshold: float = 0.3,
        energy_vad_threshold: float = 300,
    ):
        """
        :param frame_size: Number of int16 samples per audio frame.
        :param sample_rate: Audio sample rate in Hz (e.g. 16000).
        :param enable_noise_suppression: Enable Speex noise suppression.
            ``None`` (default) auto-enables if ``speexdsp_ns`` is installed.
        :param vad_enabled: Enable voice activity detection (default: True).
        :param vad_mode: WebRTC VAD aggressiveness, 0–3 (default: 2).
        :param vad_speech_threshold: Fraction of 30 ms sub-frames that must
            be classified as speech for the whole frame to count as speech
            (default: 0.3).
        :param energy_vad_threshold: RMS threshold for the energy-based VAD
            fallback.  Voices at conversational distance typically produce
            RMS > 300 on int16 scale (~-34 dBFS).  Default: 300.
        """
        self.logger = getLogger(__name__)
        self._frame_size = frame_size
        self._sample_rate = sample_rate
        self._vad_enabled = vad_enabled
        self._vad_speech_threshold = vad_speech_threshold
        self._energy_vad_threshold = energy_vad_threshold
        self._noise_suppressor = None
        self._vad = None

        self._init_noise_suppression(enable_noise_suppression)
        self._init_vad(vad_mode)

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

    def _init_vad(self, vad_mode: int):
        if not self._vad_enabled:
            return

        if self._has_webrtcvad():
            import webrtcvad

            self._vad = webrtcvad.Vad(vad_mode)
            self.logger.info('WebRTC VAD enabled (mode %d)', vad_mode)
        else:
            self.logger.info(
                'webrtcvad not installed, using energy-based speech detection. '
                'For better accuracy: pip install webrtcvad'
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

    def has_speech(self, data: bytes) -> bool:
        """
        Determine whether an audio frame contains speech.

        Uses WebRTC VAD when available, otherwise falls back to an
        energy-based (RMS) check.  Always returns ``True`` when VAD is
        disabled.
        """
        if not self._vad_enabled:
            return True

        if self._vad is not None:
            return self._webrtcvad_check(data)
        return self._energy_vad_check(data)

    # ------------------------------------------------------------------
    # VAD implementations
    # ------------------------------------------------------------------

    def _webrtcvad_check(self, data: bytes) -> bool:
        """
        Split the frame into 30 ms sub-frames and return ``True`` if the
        fraction of speech sub-frames meets the threshold.
        """
        sub_frame_samples = int(self._sample_rate * 30 / 1000)  # 30 ms
        sub_frame_bytes = sub_frame_samples * 2  # int16 = 2 bytes/sample
        num_sub_frames = len(data) // sub_frame_bytes

        if num_sub_frames == 0:
            return False

        speech_count = sum(
            1
            for i in range(num_sub_frames)
            if self._vad
            and self._vad.is_speech(
                data[i * sub_frame_bytes : (i + 1) * sub_frame_bytes],
                self._sample_rate,
            )
        )

        return (speech_count / num_sub_frames) >= self._vad_speech_threshold

    def _energy_vad_check(self, data: bytes) -> bool:
        """
        Simple energy-based fallback.  Returns ``True`` if the RMS energy
        exceeds the configured threshold.
        """
        samples = np.frombuffer(data, dtype=np.int16).astype(np.float64)
        if len(samples) == 0:
            return False
        rms = np.sqrt(np.mean(samples**2))
        return rms > self._energy_vad_threshold


# vim:sw=4:ts=4:et:
