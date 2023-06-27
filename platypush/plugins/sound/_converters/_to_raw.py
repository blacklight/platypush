from typing import Iterable
from typing_extensions import override

from ._base import AudioConverter


class RawOutputAudioConverter(AudioConverter):
    """
    Converts input audio to raw audio output.
    """

    @property
    @override
    def _input_format_args(self) -> Iterable[str]:
        return self._compressed_ffmpeg_args

    @property
    @override
    def _output_format_args(self) -> Iterable[str]:
        return self._raw_ffmpeg_args


class RawOutputAudioFromFileConverter(RawOutputAudioConverter):
    """
    Converts an input file to raw audio output.
    """

    def __init__(self, *args, infile: str, **kwargs):
        super().__init__(*args, **kwargs)
        self.infile = infile

    @property
    @override
    def _input_source_args(self) -> Iterable[str]:
        return ('-i', self.infile)


# vim:sw=4:ts=4:et:
