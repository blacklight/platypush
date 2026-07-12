import subprocess
from io import BytesIO
from dataclasses import dataclass, field
from typing import List

import numpy as np

from platypush.common.assistant import AudioFrame


@dataclass
class RecordingState:
    """
    Current state of the audio recording.
    """

    sample_rate: int
    channels: int
    silence_duration: float = 0.0
    audio_frames: List[np.ndarray] = field(default_factory=list)
    duration: float = 0.0
    conversation_started: bool = False

    def _frame_duration(self, data: np.ndarray) -> float:
        return len(data) / (self.sample_rate * self.channels)

    def add_audio(self, audio: AudioFrame, is_speech: bool = True):
        frame_dur = self._frame_duration(audio.data)
        self.audio_frames.append(audio.data)
        self.duration += frame_dur

        if is_speech:
            self.conversation_started = True
            self.silence_duration = 0.0
        else:
            self.silence_duration += frame_dur

    def is_silent(self) -> bool:
        return not self.conversation_started

    def export_audio(self) -> BytesIO:
        buffer = BytesIO()
        if not self.audio_frames:
            return buffer

        pcm = np.concatenate(self.audio_frames)
        proc = subprocess.run(
            [
                'ffmpeg',
                '-f',
                's16le',
                '-ar',
                str(self.sample_rate),
                '-ac',
                str(self.channels),
                '-i',
                'pipe:',
                '-f',
                'mp3',
                '-b:a',
                '92k',
                'pipe:',
            ],
            input=pcm.tobytes(),
            capture_output=True,
            check=True,
        )
        buffer.write(proc.stdout)
        return buffer

    def reset(self):
        self.audio_frames.clear()
        self.duration = 0.0
        self.silence_duration = 0.0
        self.conversation_started = False
