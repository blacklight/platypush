import functools
import mimetypes
import os

from platypush.utils import get_mime_type

from . import MediaHandler


class FileHandler(MediaHandler):
    """
    Handler for local media files.
    """

    prefix_handlers = ['file://']

    def __init__(self, source, *args, **kwargs):
        super().__init__(source, *args, **kwargs)

        self.path = os.path.abspath(
            os.path.expanduser(self.source[len(self._matched_handler) :])
        )
        self.filename = self.path.split('/')[-1]

        if not os.path.isfile(self.path):
            raise FileNotFoundError(self.path)

        self.mime_type = get_mime_type(source)
        assert self.mime_type, f'Could not detect mime type for {source}'
        assert (
            self.mime_type[:5] in ['video', 'audio', 'image']
            or self.mime_type == 'application/octet-stream'
        ), f'{source} is not a valid media file (detected format: {self.mime_type})'

        self.extension = mimetypes.guess_extension(self.mime_type)
        if self.url and self.extension:
            self.url += self.extension
        self.content_length = os.path.getsize(self.path)

    def get_data(self, from_bytes=None, to_bytes=None, chunk_size=None):
        if from_bytes is None:
            from_bytes = 0
        if to_bytes is None:
            to_bytes = os.path.getsize(self.path)
        if chunk_size is None:
            chunk_size = os.path.getsize(self.path) - from_bytes

        with open(self.path, 'rb') as f:
            f.seek(from_bytes)
            for chunk in iter(
                functools.partial(f.read, min(to_bytes - from_bytes, chunk_size)), b''
            ):
                yield chunk


# vim:sw=4:ts=4:et:
