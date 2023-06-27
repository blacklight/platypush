from typing import Optional, Type
from typing_extensions import override

from platypush.message.event.sound import SoundEvent

from ..._converters import RawOutputAudioFromFileConverter
from ._base import AudioPlayer


class AudioResourcePlayer(AudioPlayer):
    """
    A ``AudioResourcePlayer`` thread is responsible for playing an audio
    resource - either a file or a URL.
    """

    @property
    @override
    def _audio_converter_type(self) -> Type[RawOutputAudioFromFileConverter]:
        return RawOutputAudioFromFileConverter

    @property
    @override
    def _converter_args(self) -> dict:
        return {
            'infile': self.infile,
            **super()._converter_args,
        }

    @property
    @override
    def _converter_stdin(self) -> Optional[int]:
        return None

    @override
    def _notify(self, event_type: Type[SoundEvent], **kwargs):
        return super()._notify(event_type, resource=self.infile, **kwargs)


# vim:sw=4:ts=4:et:
