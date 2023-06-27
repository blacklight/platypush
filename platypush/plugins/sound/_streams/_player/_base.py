from abc import ABC
from typing import IO, Iterable, List, Optional, Type, Union
from typing_extensions import override

import numpy as np
import sounddevice as sd

from platypush.message.event.sound import (
    SoundPlaybackPausedEvent,
    SoundPlaybackResumedEvent,
    SoundPlaybackStartedEvent,
    SoundPlaybackStoppedEvent,
)

from ..._converters import RawOutputAudioConverter
from ..._model import StreamType
from .._base import AudioThread


class AudioPlayer(AudioThread, ABC):
    """
    Base ``AudioPlayer`` class.

    An ``AudioPlayer`` thread is responsible for playing audio (either from a
    file/URL or from a synthetic source) to an output device, writing it to the
    converter process and dispatching the converted audio to the registered
    consumers.
    """

    def __init__(
        self, *args, sound: Optional[Union[dict, Iterable[dict]]] = None, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.sound = sound

    @classmethod
    def build(
        cls,
        infile: Optional[str] = None,
        sound: Optional[Union[dict, Iterable[dict]]] = None,
        **kwargs,
    ) -> "AudioPlayer":
        from ._resource import AudioResourcePlayer
        from ._synth import AudioSynthPlayer, Sound

        if infile:
            return AudioResourcePlayer(infile=infile, **kwargs)
        if sound:
            sounds: List[dict] = (  # type: ignore
                [sound] if isinstance(sound, dict) else sound
            )

            return AudioSynthPlayer(sounds=[Sound.build(**s) for s in sounds], **kwargs)

        raise AssertionError('Either infile or url must be specified')

    @property
    @override
    def direction(self) -> StreamType:
        return StreamType.OUTPUT

    @override
    def _on_converter_timeout(self, *_, **__) -> bool:
        return False  # break

    @property
    @override
    def _stream_type(self) -> Type[sd.RawOutputStream]:
        return sd.RawOutputStream

    @property
    @override
    def _audio_converter_type(self) -> Type[RawOutputAudioConverter]:
        return RawOutputAudioConverter

    @override
    def _on_audio_converted(self, data: bytes, out_f: Optional[IO] = None):
        if self.audio_stream:
            self.audio_stream.write(
                np.asarray(
                    self.gain
                    * np.frombuffer(data, dtype=self.dtype).reshape(-1, self.channels),
                    dtype=self.dtype,
                )
            )

        super()._on_audio_converted(data, out_f)

    @property
    @override
    def _started_event_type(self) -> Type[SoundPlaybackStartedEvent]:
        return SoundPlaybackStartedEvent

    @property
    @override
    def _stopped_event_type(self) -> Type[SoundPlaybackStoppedEvent]:
        return SoundPlaybackStoppedEvent

    @property
    @override
    def _paused_event_type(self) -> Type[SoundPlaybackPausedEvent]:
        return SoundPlaybackPausedEvent

    @property
    @override
    def _resumed_event_type(self) -> Type[SoundPlaybackResumedEvent]:
        return SoundPlaybackResumedEvent


# vim:sw=4:ts=4:et:
