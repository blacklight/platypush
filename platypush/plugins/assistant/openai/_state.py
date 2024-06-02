from io import BytesIO
from dataclasses import dataclass, field
from typing import List

import numpy as np
from pydub import AudioSegment, silence

from platypush.common.assistant import AudioFrame


@dataclass
class RecordingState:
    """
    Current state of the audio recording.
    """

    sample_rate: int
    channels: int
    min_silence_secs: float
    silence_threshold: int
    silence_duration: float = 0.0
    audio_segments: List[AudioSegment] = field(default_factory=list)
    duration: float = 0.0
    conversation_started: bool = False

    def _silence_duration(self, audio: AudioSegment) -> float:
        silent_frames = [
            (start / 1000, stop / 1000)
            for start, stop in silence.detect_silence(
                audio,
                min_silence_len=int(self.min_silence_secs * 1000),
                silence_thresh=int(self.silence_threshold),
            )
        ]

        return sum(stop - start for start, stop in silent_frames)

    def _to_audio_segment(self, data: np.ndarray) -> AudioSegment:
        return AudioSegment(
            data.tobytes(),
            frame_rate=self.sample_rate,
            sample_width=data.dtype.itemsize,
            channels=self.channels,
        )

    def _add_audio_segment(self, audio: AudioSegment):
        self.audio_segments.append(audio)
        self.duration += audio.duration_seconds
        silence_duration = self._silence_duration(audio)
        is_mostly_silent = silence_duration >= audio.duration_seconds * 0.75

        if is_mostly_silent:
            self.silence_duration += silence_duration
        else:
            self.conversation_started = True
            self.silence_duration = 0.0

    def is_silent(self) -> bool:
        return self.silence_duration >= self.duration

    def add_audio(self, audio: AudioFrame):
        self._add_audio_segment(self._to_audio_segment(audio.data))

    def export_audio(self) -> BytesIO:
        buffer = BytesIO()
        if not self.audio_segments:
            return buffer

        audio = self.audio_segments[0]
        for segment in self.audio_segments[1:]:
            audio += segment

        audio.export(buffer, format="mp3", bitrate='92')
        return buffer

    def reset(self):
        self.audio_segments.clear()
        self.duration = 0.0
        self.silence_duration = 0.0
        self.conversation_started = False
