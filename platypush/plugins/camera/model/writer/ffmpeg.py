import subprocess
import threading
import time

from abc import ABC
from typing import Optional, Tuple

from platypush.plugins.camera.model.camera import Camera
from platypush.plugins.camera.model.writer import (
    VideoWriter,
    FileVideoWriter,
    StreamWriter,
)


class FFmpegWriter(VideoWriter, ABC):
    """
    Generic FFmpeg encoder for camera frames.
    """

    def __init__(
        self,
        *args,
        input_file: str = '-',
        input_format: str = 'rawvideo',
        output_file: str = '-',
        output_format: Optional[str] = None,
        pix_fmt: Optional[str] = None,
        output_opts: Optional[Tuple] = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.input_file = input_file
        self.input_format = input_format
        self.output_format = output_format
        self.output_file = output_file
        self.width, self.height = self.camera.effective_resolution()
        self.pix_fmt = pix_fmt
        self.output_opts = output_opts or ()

        self.logger.info('Starting FFmpeg. Command: ' + ' '.join(self.ffmpeg_args))
        self.ffmpeg = subprocess.Popen(
            self.ffmpeg_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE
        )

    @property
    def ffmpeg_args(self):
        return [
            self.camera.info.ffmpeg_bin,
            '-y',
            '-f',
            self.input_format,
            *(('-pix_fmt', self.pix_fmt) if self.pix_fmt else ()),
            '-s',
            f'{self.width}x{self.height}',
            '-r',
            str(self.camera.info.fps),
            '-i',
            self.input_file,
            *(('-f', self.output_format) if self.output_format else ()),
            *self.output_opts,
            *(
                ('-vcodec', self.camera.info.output_codec)
                if self.camera.info.output_codec
                else ()
            ),
            self.output_file,
        ]

    def is_closed(self):
        return self.closed or not self.ffmpeg or self.ffmpeg.poll() is not None

    def write(self, image):
        if self.is_closed():
            return

        try:
            self.ffmpeg.stdin.write(image.convert('RGB').tobytes())
        except Exception as e:
            self.logger.warning('FFmpeg send error: %s', e)
            self.close()

    def close(self):
        if not self.is_closed():
            if self.ffmpeg and self.ffmpeg.stdin:
                try:
                    self.ffmpeg.stdin.close()
                except OSError:
                    pass

            if self.ffmpeg:
                self.ffmpeg.terminate()
                try:
                    self.ffmpeg.wait(timeout=5.0)
                except subprocess.TimeoutExpired:
                    self.logger.warning('FFmpeg has not returned - killing it')
                    self.ffmpeg.kill()

            if self.ffmpeg and self.ffmpeg.stdout:
                try:
                    self.ffmpeg.stdout.close()
                except OSError:
                    pass

        self.ffmpeg = None
        super().close()


class FFmpegFileWriter(FileVideoWriter, FFmpegWriter):
    """
    Write camera frames to a file using FFmpeg.
    """

    def __init__(self, *args, output_file: str, **kwargs):
        super().__init__(*args, output_file=output_file, pix_fmt='rgb24', **kwargs)


class FFmpegStreamWriter(StreamWriter, FFmpegWriter, ABC):
    """
    Stream camera frames using FFmpeg.
    """

    def __init__(
        self, *args, output_format: str, output_opts: Optional[Tuple] = None, **kwargs
    ):
        super().__init__(
            *args,
            pix_fmt='rgb24',
            output_format=output_format,
            output_opts=output_opts
            or (
                '-tune',
                'zerolatency',
                '-preset',
                'superfast',
                '-trellis',
                '0',
                '-fflags',
                'nobuffer',
            ),
            **kwargs,
        )
        self._reader = threading.Thread(target=self._reader_thread)
        self._reader.start()

    def encode(self, image) -> bytes:
        return image.convert('RGB').tobytes()

    def _reader_thread(self):
        start_time = time.time()

        while not self.is_closed():
            try:
                data = self.ffmpeg.stdout.read(1 << 15)
            except Exception as e:
                self.logger.warning('FFmpeg reader error: %s', e)
                break

            if not data:
                continue

            if self.frame is None:
                latency = time.time() - start_time
                self.logger.info('FFmpeg stream latency: %d secs', latency)

            with self.ready:
                self.frame = data
                self.frame_time = time.time()
                self.ready.notify_all()

            self._sock_send(self.frame)

    def write(self, image):
        if self.is_closed():
            return

        data = self.encode(image)
        try:
            self.ffmpeg.stdin.write(data)
        except Exception as e:
            self.logger.warning('FFmpeg send error: %s', e)
            self.close()

    def close(self):
        super().close()
        if (
            self._reader
            and self._reader.is_alive()
            and threading.get_ident() != self._reader.ident
        ):
            self._reader.join(timeout=5.0)
            self._reader = None


class MKVStreamWriter(FFmpegStreamWriter):
    mimetype = 'video/webm'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, output_format='matroska', **kwargs)


class H264StreamWriter(FFmpegStreamWriter):
    mimetype = 'video/h264'

    def __init__(self, camera: Camera, *args, **kwargs):
        if not camera.info.output_codec:
            camera.info.output_codec = 'libxvid'
        super().__init__(camera, *args, output_format='h264', **kwargs)


class H265StreamWriter(FFmpegStreamWriter):
    mimetype = 'video/h265'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, output_format='h265', **kwargs)


# vim:sw=4:ts=4:et:
