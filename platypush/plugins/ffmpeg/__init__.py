import os
import subprocess
import threading
from typing import Callable, Optional, List

from platypush.plugins import Plugin, action


class FfmpegPlugin(Plugin):
    """
    Generic FFmpeg plugin to interact with media files and devices.

    Requires:

        * **ffmpeg-python** (``pip install ffmpeg-python``)
        * The **ffmpeg** package installed on the system.

    """

    def __init__(self, ffmpeg_cmd: str = 'ffmpeg', ffprobe_cmd: str = 'ffprobe', **kwargs):
        super().__init__(**kwargs)
        self.ffmpeg_cmd = ffmpeg_cmd
        self.ffprobe_cmd = ffprobe_cmd
        self._threads = {}
        self._next_thread_id = 1
        self._thread_lock = threading.RLock()

    @action
    def info(self, filename: str, **kwargs) -> dict:
        """
        Get the information of a media file.

        :param filename: Path to the media file.
        :return: Media file information. Example:

          .. code-block:: json

              {
                "streams": [
                    {
                        "index": 0,
                        "codec_name": "h264",
                        "codec_long_name": "H.264 / AVC / MPEG-4 AVC / MPEG-4 part 10",
                        "profile": "High 4:2:2",
                        "codec_type": "video",
                        "codec_time_base": "1/60",
                        "codec_tag_string": "[0][0][0][0]",
                        "codec_tag": "0x0000",
                        "width": 640,
                        "height": 480,
                        "coded_width": 640,
                        "coded_height": 480,
                        "closed_captions": 0,
                        "has_b_frames": 2,
                        "pix_fmt": "yuv422p",
                        "level": 30,
                        "chroma_location": "left",
                        "field_order": "progressive",
                        "refs": 1,
                        "is_avc": "true",
                        "nal_length_size": "4",
                        "r_frame_rate": "30/1",
                        "avg_frame_rate": "30/1",
                        "time_base": "1/1000",
                        "start_pts": 0,
                        "start_time": "0.000000",
                        "bits_per_raw_sample": "8",
                        "disposition": {
                            "default": 1,
                            "dub": 0,
                            "original": 0,
                            "comment": 0,
                            "lyrics": 0,
                            "karaoke": 0,
                            "forced": 0,
                            "hearing_impaired": 0,
                            "visual_impaired": 0,
                            "clean_effects": 0,
                            "attached_pic": 0,
                            "timed_thumbnails": 0
                        },
                        "tags": {
                            "ENCODER": "Lavc58.91.100 libx264"
                        }
                    }
                ],
                "format": {
                    "filename": "./output.mkv",
                    "nb_streams": 1,
                    "nb_programs": 0,
                    "format_name": "matroska,webm",
                    "format_long_name": "Matroska / WebM",
                    "start_time": "0.000000",
                    "size": "786432",
                    "probe_score": 100,
                    "tags": {
                        "ENCODER": "Lavf58.45.100"
                    }
                }
            }

        """
        # noinspection PyPackageRequirements
        import ffmpeg
        filename = os.path.abspath(os.path.expanduser(filename))
        info = ffmpeg.probe(filename, cmd=self.ffprobe_cmd, **kwargs)
        return info

    @staticmethod
    def _poll_thread(proc: subprocess.Popen, packet_size: int, on_packet: Callable[[bytes], None],
                     on_open: Optional[Callable[[], None]] = None,
                     on_close: Optional[Callable[[], None]] = None):
        try:
            if on_open:
                on_open()

            while proc.poll() is None:
                data = proc.stdout.read(packet_size)
                on_packet(data)
        finally:
            if on_close:
                on_close()

    @action
    def start(self, pipeline: List[dict], pipe_stdin: bool = False, pipe_stdout: bool = False,
              pipe_stderr: bool = False, quiet: bool = False, overwrite_output: bool = False,
              on_packet: Callable[[bytes], None] = None, packet_size: int = 4096):
        # noinspection PyPackageRequirements
        import ffmpeg
        stream = ffmpeg

        for step in pipeline:
            args = step.pop('args') if 'args' in step else []
            stream = getattr(stream, step.pop('method'))(*args, **step)

        self.logger.info('Executing {cmd} {args}'.format(cmd=self.ffmpeg_cmd, args=stream.get_args()))
        proc = stream.run_async(cmd=self.ffmpeg_cmd, pipe_stdin=pipe_stdin, pipe_stdout=pipe_stdout,
                                pipe_stderr=pipe_stderr, quiet=quiet, overwrite_output=overwrite_output)

        if on_packet:
            with self._thread_lock:
                self._threads[self._next_thread_id] = threading.Thread(target=self._poll_thread, kwargs=dict(
                    proc=proc, on_packet=on_packet, packet_size=packet_size))
                self._threads[self._next_thread_id].start()
                self._next_thread_id += 1


# vim:sw=4:ts=4:et:
