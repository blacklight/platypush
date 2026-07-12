from io import BytesIO
from dataclasses import dataclass, field
from typing import List

import numpy as np
from pydub import AudioSegment

from platypush.common.assistant import AudioFrame


@dataclass
class RecordingState:
    """
    Current state of the audio recording.
    """

    sample_rate: int
    channels: int
    silence_duration: float = 0.0
    audio_segments: List[AudioSegment] = field(default_factory=list)
    duration: float = 0.0
    conversation_started: bool = False

    def _to_audio_segment(self, data: np.ndarray) -> AudioSegment:
        return AudioSegment(
            data.tobytes(),
            frame_rate=self.sample_rate,
            sample_width=data.dtype.itemsize,
            channels=self.channels,
        )

    def _add_audio_segment(self, audio: AudioSegment, is_speech: bool):
        self.audio_segments.append(audio)
        self.duration += audio.duration_seconds

        if is_speech:
            self.conversation_started = True
            self.silence_duration = 0.0
        else:
            self.silence_duration += audio.duration_seconds

    def is_silent(self) -> bool:
        return not self.conversation_started

    def add_audio(self, audio: AudioFrame, is_speech: bool = True):
        self._add_audio_segment(self._to_audio_segment(audio.data), is_speech)

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
