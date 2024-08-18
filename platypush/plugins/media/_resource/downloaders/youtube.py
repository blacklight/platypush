import json
import signal
import subprocess
import threading
from contextlib import suppress
from typing import Optional

from platypush.plugins.media._model import DownloadState
from platypush.plugins.media._resource import MediaResource, YoutubeMediaResource
from platypush.utils import wait_for_either

from ._base import DownloadThread, MediaResourceDownloader


class YoutubeResourceDownloader(MediaResourceDownloader):
    """
    Downloader for YouTube URLs.
    """

    def supports(self, resource_type: MediaResource) -> bool:
        return isinstance(resource_type, YoutubeMediaResource)

    def download(  # type: ignore[override]
        self,
        resource: YoutubeMediaResource,
        path: str,
        youtube_format: Optional[str] = None,
        youtube_audio_format: Optional[str] = None,
        merge_output_format: Optional[str] = None,
        only_audio: bool = False,
        **_,
    ) -> 'YouTubeDownloadThread':
        path = self.get_download_path(
            resource=resource, directory=path, youtube_format=youtube_format
        )

        download_thread = YouTubeDownloadThread(
            url=resource.url,
            path=path,
            ytdl=self._media._ytdl,  # pylint: disable=protected-access
            only_audio=only_audio,
            youtube_format=youtube_format or self._media.youtube_format,
            youtube_audio_format=youtube_audio_format
            or self._media.youtube_audio_format,
            merge_output_format=merge_output_format or self._media.merge_output_format,
            on_start=self._media.on_download_start,
            post_event=self._media.post_event,
            stop_event=self._media._should_stop,  # pylint: disable=protected-access
        )

        self._media.start_download(download_thread)
        return download_thread

    def get_download_path(
        self,
        resource: YoutubeMediaResource,
        *_,
        directory: Optional[str] = None,
        filename: Optional[str] = None,
        youtube_format: Optional[str] = None,
        **__,
    ) -> str:
        youtube_format = youtube_format or self._media.youtube_format

        if not filename:
            filename = resource.filename

        if not filename:
            with subprocess.Popen(
                [
                    self._media._ytdl,  # pylint: disable=protected-access
                    *(
                        [
                            '-f',
                            youtube_format,
                        ]
                        if youtube_format
                        else []
                    ),
                    '-O',
                    '%(title)s.%(ext)s',
                    resource.url,
                ],
                stdout=subprocess.PIPE,
            ) as proc:
                assert proc.stdout, 'yt-dlp stdout is None'
                filename = proc.stdout.read().decode()[:-1]

        return super().get_download_path(
            resource, directory=directory, filename=filename
        )

    def supports_only_audio(self) -> bool:
        return True


class YouTubeDownloadThread(DownloadThread):
    """
    Thread that downloads a YouTube URL to a file.
    """

    def __init__(
        self,
        *args,
        ytdl: str,
        youtube_format: Optional[str] = None,
        youtube_audio_format: Optional[str] = None,
        merge_output_format: Optional[str] = None,
        only_audio: bool = False,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self._ytdl = ytdl
        self._youtube_format = youtube_format
        self._youtube_audio_format = youtube_audio_format
        self._merge_output_format = merge_output_format
        self._only_audio = only_audio
        self._proc = None
        self._proc_lock = threading.Lock()

    def _parse_progress(self, line: str):
        try:
            progress = json.loads(line)
        except json.JSONDecodeError:
            return

        status = progress.get('status')
        if not status:
            return

        if status == 'finished':
            self.progress = 100
            return

        if status == 'paused':
            self.state = DownloadState.PAUSED
        elif status == 'downloading':
            self.state = DownloadState.DOWNLOADING

        self.size = int(progress.get('total_bytes_estimate', 0)) or self.size
        if self.size:
            downloaded = int(progress.get('downloaded_bytes', 0))
            self.progress = (downloaded / self.size) * 100

    def _run(self):
        youtube_format = (
            self._youtube_audio_format if self._only_audio else self._youtube_format
        )

        ytdl_cmd = [
            self._ytdl,
            '--newline',
            '--progress',
            '--progress-delta',
            str(self._progress_update_interval),
            '--progress-template',
            '%(progress)j',
            *(['-x'] if self._only_audio else []),
            *(['-f', youtube_format] if youtube_format else []),
            self.url,
            '-o',
            self.path,
        ]

        self.logger.info('Executing command %r', ytdl_cmd)
        err = None

        with subprocess.Popen(ytdl_cmd, stdout=subprocess.PIPE) as self._proc:
            if self._proc.stdout:
                for line in self._proc.stdout:
                    self.logger.debug(
                        '%s output: %s', self._ytdl, line.decode().strip()
                    )

                    self._parse_progress(line.decode())

                    if self.should_stop():
                        self.stop()
                        return self._proc.returncode == 0

                    if self._paused.is_set():
                        wait_for_either(self._downloading, self._stop_event)

        if self._proc.returncode != 0:
            err = self._proc.stderr.read().decode() if self._proc.stderr else None
            raise RuntimeError(
                f'{self._ytdl} failed with return code {self._proc.returncode}: {err}'
            )

        return True

    def pause(self):
        with self._proc_lock:
            if self._proc:
                self._proc.send_signal(signal.SIGSTOP)

        super().pause()

    def resume(self):
        with self._proc_lock:
            if self._proc:
                self._proc.send_signal(signal.SIGCONT)

        super().resume()

    def stop(self):
        state = None

        with suppress(IOError, OSError), self._proc_lock:
            if self._proc:
                if self._proc.poll() is None:
                    self._proc.terminate()
                    self._proc.wait(timeout=3)
                    if self._proc.returncode is None:
                        self._proc.kill()

                    state = DownloadState.CANCELLED
                elif self._proc.returncode != 0:
                    state = DownloadState.ERROR
                else:
                    state = DownloadState.COMPLETED

                self._proc = None

        super().stop()

        if state:
            self.state = state

    def on_close(self):
        self.stop()
        super().on_close()
