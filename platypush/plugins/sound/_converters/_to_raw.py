from typing import Iterable

from ._base import AudioConverter, dtype_to_ffmpeg_format


class RawOutputAudioConverter(AudioConverter):
    """
    Converts input audio to raw audio output.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self._dtype and not self._output_format:
            ffmpeg_format = dtype_to_ffmpeg_format.get(self._dtype)
            assert ffmpeg_format, (
                f'Unsupported data type: {self._dtype}. Supported data types: '
                f'{list(dtype_to_ffmpeg_format.keys())}'
            )

            self._output_format = ffmpeg_format

    @property
    def _input_format_args(self) -> Iterable[str]:
        if not self._input_format:
            return ()

        ffmpeg_args = self._format_to_ffmpeg_args.get(self._input_format)
        if not ffmpeg_args:
            return ('-f', self._input_format)

        return ffmpeg_args

    @property
    def _output_format_args(self) -> Iterable[str]:
        args = (
            '-ar',
            str(self._sample_rate),
            *self._channel_layout_args,
        )

        if self._output_format:
            args = ('-f', self._output_format) + args

        return args


class RawOutputAudioFromFileConverter(RawOutputAudioConverter):
    """
    Converts an input file to raw audio output.
    """

    def __init__(self, *args, infile: str, **kwargs):
        super().__init__(*args, **kwargs)
        self.infile = infile

    @property
    def _input_source_args(self) -> Iterable[str]:
        return ('-i', self.infile)


# vim:sw=4:ts=4:et:
