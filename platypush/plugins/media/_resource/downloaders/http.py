from typing import Optional
import requests

from platypush.plugins.media._resource import HttpMediaResource, MediaResource
from platypush.utils import wait_for_either

from ._base import DownloadState, DownloadThread, MediaResourceDownloader


class HttpResourceDownloader(MediaResourceDownloader):
    """
    Downloader for generic HTTP URLs.
    """

    def supports(self, resource_type: MediaResource) -> bool:  # type: ignore[override]
        return isinstance(resource_type, HttpMediaResource)

    def download(  # type: ignore[override]
        self,
        resource: HttpMediaResource,
        path: Optional[str] = None,
        timeout: Optional[int] = None,
        **_
    ) -> 'HttpDownloadThread':
        path = path or self.get_download_path(resource=resource)
        download_thread = HttpDownloadThread(
            url=resource.url,
            path=path,
            timeout=timeout,
            on_start=self._media.on_download_start,
            post_event=self._media.post_event,
            stop_event=self._media._should_stop,  # pylint: disable=protected-access
        )

        self._media.start_download(download_thread)
        return download_thread


class HttpDownloadThread(DownloadThread):
    """
    Thread that downloads a generic URL to a file.
    """

    def _run(self):
        interrupted = False

        with requests.get(self.url, timeout=self.timeout, stream=True) as response:
            response.raise_for_status()
            self.size = int(response.headers.get('Content-Length', 0)) or None

            with open(self.path, 'wb') as f:
                self.on_start()

                for chunk in response.iter_content(chunk_size=8192):
                    if not chunk or self.should_stop():
                        interrupted = self.should_stop()
                        if interrupted:
                            self.stop()

                        break

                    self.state = DownloadState.DOWNLOADING
                    f.write(chunk)
                    percent = f.tell() / self.size * 100 if self.size else 0
                    self.progress = percent

                    if self._paused.is_set():
                        wait_for_either(self._downloading, self._stop_event)

        return not interrupted


# vim:sw=4:ts=4:et:
