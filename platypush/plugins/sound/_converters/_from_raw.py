from typing import Iterable

from ._base import AudioConverter, dtype_to_ffmpeg_format


class RawInputAudioConverter(AudioConverter):
    """
    Converts raw audio input to a compressed media format.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self._dtype and not self._input_format:
            ffmpeg_format = dtype_to_ffmpeg_format.get(self._dtype)
            assert ffmpeg_format, (
                f'Unsupported data type: {self._dtype}. Supported data types: '
                f'{list(dtype_to_ffmpeg_format.keys())}'
            )

            self._input_format = ffmpeg_format

    @property
    def _input_format_args(self) -> Iterable[str]:
        args = (
            '-ar',
            str(self._sample_rate),
            *self._channel_layout_args,
        )

        if self._input_format:
            args = ('-f', self._input_format) + args

        return args

    @property
    def _output_format_args(self) -> Iterable[str]:
        if not self._output_format:
            return ()

        ffmpeg_args = self._format_to_ffmpeg_args.get(self._output_format)
        assert ffmpeg_args, (
            f'Unsupported output format: {self._output_format}. Supported formats: '
            f'{list(self._format_to_ffmpeg_args.keys())}'
        )

        return ffmpeg_args


# vim:sw=4:ts=4:et:
