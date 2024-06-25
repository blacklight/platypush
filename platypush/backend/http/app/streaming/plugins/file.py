import os
from contextlib import contextmanager
from datetime import datetime as dt
from typing import Optional, Tuple

from tornado.web import stream_request_body

from platypush.utils import get_mime_type

from .. import StreamingRoute


@stream_request_body
class FileRoute(StreamingRoute):
    """
    Generic route to read the content of a file on the server.
    """

    BUFSIZE = 1024

    @classmethod
    def path(cls) -> str:
        """
        Route: GET /file?path=<path>[&download]
        """
        return r"^/file$"

    @property
    def download(self) -> bool:
        return 'download' in self.request.arguments

    @property
    def file_path(self) -> str:
        return os.path.expanduser(
            self.request.arguments.get('path', [b''])[0].decode('utf-8')
        )

    @property
    def file_size(self) -> int:
        return os.path.getsize(self.file_path)

    @property
    def range(self) -> Tuple[Optional[int], Optional[int]]:
        range_hdr = self.request.headers.get('Range')
        if not range_hdr:
            return None, None

        start, end = range_hdr.split('=')[-1].split('-')
        start = int(start) if start else 0
        end = int(end) if end else self.file_size - 1
        return start, end

    def set_headers(self):
        self.set_header('Content-Length', str(os.path.getsize(self.file_path)))
        self.set_header(
            'Content-Type', get_mime_type(self.file_path) or 'application/octet-stream'
        )
        self.set_header('Accept-Ranges', 'bytes')
        self.set_header(
            'Last-Modified',
            dt.fromtimestamp(os.path.getmtime(self.file_path)).strftime(
                '%a, %d %b %Y %H:%M:%S GMT'
            ),
        )

        if self.download:
            self.set_header(
                'Content-Disposition',
                f'attachment; filename="{os.path.basename(self.file_path)}"',
            )

        if self.range[0] is not None:
            start, end = self.range
            self.set_header(
                'Content-Range',
                f'bytes {start}-{end}/{self.file_size}',
            )
            self.set_status(206)

    @contextmanager
    def _serve(self):
        path = self.file_path
        if not path:
            self.write_error(400, 'Missing path argument')
            return

        self.logger.debug('Received file read request for %r', path)

        try:
            with open(path, 'rb') as f:
                self.set_headers()
                yield f
        except FileNotFoundError:
            self.write_error(404, 'File not found')
            yield
            return
        except PermissionError:
            self.write_error(403, 'Permission denied')
            yield
            return
        except Exception as e:
            self.write_error(500, str(e))
            yield
            return

        self.finish()

    def get(self) -> None:
        with self._serve() as f:
            if f:
                while True:
                    chunk = f.read(self.BUFSIZE)
                    if not chunk:
                        break

                    self.write(chunk)
                    self.flush()

    def head(self) -> None:
        with self._serve():
            pass
