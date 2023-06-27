from typing import Iterable
from typing_extensions import override

from ._base import AudioConverter


class RawInputAudioConverter(AudioConverter):
    """
    Converts raw audio input to a compressed media format.
    """

    @property
    @override
    def _input_format_args(self) -> Iterable[str]:
        return self._raw_ffmpeg_args

    @property
    @override
    def _output_format_args(self) -> Iterable[str]:
        return self._compressed_ffmpeg_args


# vim:sw=4:ts=4:et:
