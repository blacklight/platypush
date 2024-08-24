import os
import pathlib
from contextlib import contextmanager
from datetime import datetime as dt
from typing import IO, Optional, Tuple

from tornado.web import stream_request_body

from platypush.utils import get_mime_type

from .. import StreamingRoute


@stream_request_body
class FileRoute(StreamingRoute):
    """
    Generic route to read the content of a file on the server.
    """

    BUFSIZE = 1024
    _bytes_written = 0
    _out_f: Optional[IO[bytes]] = None

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
    def _content_length(self) -> int:
        return int(self.request.headers.get('Content-Length', 0))

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

    def on_finish(self) -> None:
        if self._out_f:
            try:
                if not (self._out_f and self._out_f.closed):
                    self._out_f.close()
            except Exception as e:
                self.logger.warning('Error while closing the output file: %s', e)

            self._out_f = None

        return super().on_finish()

    def _validate_upload(self, force: bool = False) -> bool:
        if not self.file_path:
            self.write_error(400, 'Missing path argument')
            return False

        if not self._out_f:
            if not force and os.path.exists(self.file_path):
                self.write_error(409, f'{self.file_path} already exists')
                return False

            self._bytes_written = 0
            dir_path = os.path.dirname(self.file_path)

            try:
                pathlib.Path(dir_path).mkdir(parents=True, exist_ok=True)
                self._out_f = open(  # pylint: disable=consider-using-with
                    self.file_path, 'wb'
                )
            except PermissionError:
                self.write_error(403, 'Permission denied')
                return False

        return True

    def finish(self, *args, **kwargs):  # type: ignore
        try:
            return super().finish(*args, **kwargs)
        except Exception as e:
            self.logger.warning('Error while finishing the request: %s', e)

    def data_received(self, chunk: bytes):
        # Ignore unless we're in POST/PUT mode
        if self.request.method not in ('POST', 'PUT'):
            return

        force = self.request.method == 'PUT'
        if not self._validate_upload(force=force):
            self.finish()
            return

        if not chunk:
            self.logger.debug('Received EOF from client')
            self.finish()
            return

        assert self._out_f
        self._out_f.write(chunk)
        self._out_f.flush()
        self._bytes_written += len(chunk)
        self.logger.debug(
            'Written chunk of size %d to %s, progress: %d/%d',
            len(chunk),
            self.file_path,
            self._bytes_written,
            self._content_length,
        )

        self.flush()

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

    def post(self) -> None:
        self.logger.info('Receiving file POST upload request for %r', self.file_path)

    def put(self) -> None:
        self.logger.info('Receiving file PUT upload request for %r', self.file_path)
