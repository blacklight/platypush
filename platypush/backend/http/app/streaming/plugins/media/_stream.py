import json
from typing import Optional

from tornado.web import stream_request_body

from platypush.backend.http.app.streaming import StreamingRoute

from ._constants import STREAMING_BLOCK_SIZE, STREAMING_CHUNK_SIZE
from ._register import register_media
from ._registry import load_media_map
from ._unregister import unregister_media


@stream_request_body
class MediaStreamRoute(StreamingRoute):
    """
    Route for media streams.
    """

    SUPPORTED_METHODS = ['GET', 'PUT', 'DELETE']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._body = b''

    @classmethod
    def path(cls) -> str:
        return r"^/media/?([a-zA-Z0-9_.]+)?$"

    @property
    def auth_required(self) -> bool:
        return False

    def get(self, media_id: Optional[str] = None):
        """
        Streams a media resource by ID.
        """

        # Return the list of registered streaming media resources if no ID is
        # specified
        if not media_id:
            self.get_media()
            return

        # Strip the extension
        media_id = '.'.join(media_id.split('.')[:-1])

        try:
            self.stream_media(media_id)
        except Exception as e:
            self._on_error(e)

    def put(self, *_, **__):
        """
        The `PUT` route is used to prepare a new media resource for streaming.
        """
        try:
            self.add_media()
        except Exception as e:
            self._on_error(e)

    def delete(self, media_id: Optional[str] = None):
        """
        Removes the given media_id from the map of streaming media.
        """
        media_info = unregister_media(media_id)
        self.write(json.dumps(media_info))

    def data_received(self, chunk: bytes):
        self._body += chunk

    def add_media(self):
        """
        Adds a new media resource to the map of streaming media.
        """
        args = {}
        try:
            args = json.loads(self._body)
        except Exception as e:
            raise AssertionError(f'Invalid JSON request: {e}') from e

        source = args.get('source')
        assert source, 'The request does not contain any source'
        subtitles = args.get('subtitles')
        media_hndl = register_media(source, subtitles)
        ret = media_hndl.to_json()
        if media_hndl.subtitles:
            ret['subtitles_url'] = f'/media/subtitles/{media_hndl.media_id}.vtt'

        self.write(json.dumps(ret))

    def get_media(self):
        """
        Returns the list of registered media resources.
        """
        self.add_header('Content-Type', 'application/json')
        self.finish(json.dumps([dict(media) for media in load_media_map().values()]))

    def stream_media(self, media_id: str):
        """
        Route to stream a media file given its ID.
        """
        media_hndl = load_media_map().get(media_id)
        if not media_hndl:
            raise FileNotFoundError(f'{media_id} is not a registered media_id')

        range_hdr = self.request.headers.get('Range')
        content_length = media_hndl.content_length

        self.add_header('Accept-Ranges', 'bytes')
        self.add_header('Content-Type', media_hndl.mime_type)

        if 'download' in self.request.arguments:
            self.add_header(
                'Content-Disposition',
                'attachment'
                + ('; filename="{media_hndl.filename}"' if media_hndl.filename else ''),
            )

        if range_hdr:
            from_bytes, to_bytes = range_hdr.replace('bytes=', '').split('-')
            from_bytes = int(from_bytes)

            if not to_bytes:
                to_bytes = content_length - 1
                content_length -= from_bytes
            else:
                to_bytes = int(to_bytes)
                content_length = to_bytes - from_bytes

            self.set_status(206)
            self.add_header(
                'Content-Range',
                f'bytes {from_bytes}-{to_bytes}/{media_hndl.content_length}',
            )
        else:
            from_bytes = 0
            to_bytes = STREAMING_BLOCK_SIZE

        self.add_header('Content-Length', str(content_length))
        for chunk in media_hndl.get_data(
            from_bytes=from_bytes,
            to_bytes=to_bytes,
            chunk_size=STREAMING_CHUNK_SIZE,
        ):
            self.write(chunk)
            self.flush()

        self.finish()
