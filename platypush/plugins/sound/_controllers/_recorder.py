from dataclasses import dataclass

from typing import IO
from typing_extensions import override

from platypush.context import get_bus
from platypush.message.event.sound import (
    SoundRecordingStartedEvent,
    SoundRecordingStoppedEvent,
)

from platypush.utils import get_redis

from .._converter import ConverterProcess
from .._model import AudioState
from ._base import AudioThread


@dataclass
class AudioRecorder(AudioThread):
    """
    The ``AudioRecorder`` thread is responsible for recording audio from the
    input device, writing it to the converter process and dispatch the
    converted audio to the registered consumers.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @override
    def _audio_callback(self, audio_converter: ConverterProcess):
        # _ = frames
        # __ = time
        def callback(indata, outdata, _, __, status):
            if self.state == AudioState.PAUSED:
                return

            if status:
                self.logger.warning('Recording callback status: %s', status)

            try:
                audio_converter.write(indata.tobytes())
            except AssertionError as e:
                self.logger.warning('Audio recorder callback error: %s', e)
                self.state = AudioState.STOPPED
                return

            if self.audio_pass_through:
                outdata[:] = indata

        return callback

    @override
    def _on_audio_converted(self, data: bytes, out_f: IO):
        out_f.write(data)
        if self.redis_queue and self.stream:
            get_redis().publish(self.redis_queue, data)

    @override
    def notify_start(self):
        super().notify_start()
        get_bus().post(SoundRecordingStartedEvent())

    @override
    def notify_stop(self):
        super().notify_stop()
        get_bus().post(SoundRecordingStoppedEvent())


# vim:sw=4:ts=4:et:
