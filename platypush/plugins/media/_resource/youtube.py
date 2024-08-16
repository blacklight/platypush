import os
import subprocess
from dataclasses import dataclass
from typing import IO, Optional

from ._base import PopenMediaResource


@dataclass
class YoutubeMediaResource(PopenMediaResource):
    """
    Models a YouTube media resource.
    """

    id: Optional[str] = None
    is_temporary: bool = False

    def _generate_file(self, merge_format: str):
        self.resource = os.path.join(
            self._media.cache_dir, f'platypush-yt-dlp-{self.id}.{merge_format}'
        )
        self.is_temporary = True

    def open(
        self,
        *args,
        youtube_format: Optional[str] = None,
        merge_output_format: Optional[str] = None,
        cache_streams: bool = False,
        **kwargs,
    ) -> IO:
        if self.proc is None:
            merge_output_format = merge_output_format or self._media.merge_output_format
            use_file = (
                not self._media.supports_local_media or cache_streams or self.resource
            )

            if use_file and not self.resource:
                self._generate_file(merge_output_format)

            output = ['-o', self.resource] if use_file else ['-o', '-']
            youtube_format = youtube_format or self._media.youtube_format
            cmd = [
                self._media._ytdl,  # pylint: disable=protected-access
                '--no-part',
                *(
                    [
                        '-f',
                        youtube_format,
                    ]
                    if youtube_format
                    else []
                ),
                *(
                    ['--merge-output-format', merge_output_format]
                    if merge_output_format
                    else []
                ),
                *output,
                self.url,
            ]

            proc_args = {}
            if not use_file:
                proc_args['stdout'] = subprocess.PIPE

            self._logger.debug('Running command: %s', ' '.join(cmd))
            self._logger.debug('Media resource: %s', self.to_dict())
            self.proc = subprocess.Popen(  # pylint: disable=consider-using-with
                cmd, **proc_args
            )

            if use_file:
                self._wait_for_download_start()
                self.fd = open(  # pylint: disable=consider-using-with
                    self.resource, 'rb'
                )
            elif self.proc.stdout:
                self.fd = self.proc.stdout

        return super().open(*args, **kwargs)

    def _wait_for_download_start(self) -> None:
        self._logger.info('Waiting for download to start on file: %s', self.resource)

        while True:
            file = self.resource
            if not file:
                self._logger.info('No file found to wait for download')
                break

            if not self.proc:
                self._logger.info('No download process found to wait')
                break

            if self.proc.poll() is not None:
                self._logger.info(
                    'Download process exited with status %d', self.proc.returncode
                )
                break

            # The file must exist and be at least 1MB in size
            if os.path.exists(file) and os.path.getsize(file) > 1024 * 1024:
                self._logger.info('Download started, process PID: %s', self.proc.pid)
                break

            try:
                self.proc.wait(1)
            except subprocess.TimeoutExpired:
                pass

    def close(self) -> None:
        super().close()

        if self.is_temporary and self.resource and os.path.exists(self.resource):
            try:
                self._logger.debug('Removing temporary file: %s', self.resource)
                os.unlink(self.resource)
            except FileNotFoundError:
                pass


# vim:sw=4:ts=4:et:
