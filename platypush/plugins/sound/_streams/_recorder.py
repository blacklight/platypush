from typing import Type
from typing_extensions import override

import sounddevice as sd

from platypush.message.event.sound import (
    SoundRecordingPausedEvent,
    SoundRecordingResumedEvent,
    SoundRecordingStartedEvent,
    SoundRecordingStoppedEvent,
)

from .._converters import RawInputAudioConverter
from .._model import AudioState, StreamType
from ._base import AudioThread


class AudioRecorder(AudioThread):
    """
    The ``AudioRecorder`` thread is responsible for recording audio from the
    input device, writing it to the converter process and dispatch the
    converted audio to the registered consumers.
    """

    def __init__(self, *args, output_format: str, **kwargs):
        super().__init__(*args, **kwargs)
        self.output_format = output_format

    @property
    @override
    def direction(self) -> StreamType:
        return StreamType.INPUT

    @override
    def _audio_callback(self):
        # _ = frames
        # __ = time
        def callback(indata, outdata, _, __, status):
            if self.state != AudioState.RUNNING:
                return

            if status:
                self.logger.warning('Recording callback status: %s', status)

            if not self._converter:
                self.logger.warning(
                    'The ffmpeg converter process has already terminated'
                )
                self.notify_stop()
                raise sd.CallbackStop

            try:
                self._converter.write(indata.tobytes())
            except AssertionError as e:
                self.logger.warning('Audio converter callback error: %s', e)
                self.state = AudioState.STOPPED
                return

            if self.audio_pass_through:
                outdata[:] = indata

        return callback

    @property
    @override
    def _audio_converter_type(self) -> Type[RawInputAudioConverter]:
        return RawInputAudioConverter

    @property
    @override
    def _started_event_type(self) -> Type[SoundRecordingStartedEvent]:
        return SoundRecordingStartedEvent

    @property
    @override
    def _stopped_event_type(self) -> Type[SoundRecordingStoppedEvent]:
        return SoundRecordingStoppedEvent

    @property
    @override
    def _paused_event_type(self) -> Type[SoundRecordingPausedEvent]:
        return SoundRecordingPausedEvent

    @property
    @override
    def _resumed_event_type(self) -> Type[SoundRecordingResumedEvent]:
        return SoundRecordingResumedEvent

    @property
    @override
    def _converter_args(self) -> dict:
        return {
            'format': self.output_format,
            **super()._converter_args,
        }

    @property
    @override
    def _stream_args(self) -> dict:
        return {
            'callback': self._audio_callback(),
            **super()._stream_args,
        }


# vim:sw=4:ts=4:et:
