from contextlib import contextmanager
import json
from typing import Generator, Optional
from typing_extensions import override

from tornado.web import stream_request_body

from platypush.backend.http.app.utils import send_request
from platypush.config import Config

from .. import StreamingRoute


@stream_request_body
class SoundRoute(StreamingRoute):
    """
    Route for audio streams.
    """

    _redis_queue_prefix = f'_platypush/{Config.get("device_id") or ""}/sound'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._audio_headers_written: bool = False
        """Send the audio file headers before we send the first audio frame."""

    @override
    @classmethod
    def path(cls) -> str:
        return r"/sound/stream\.?([a-zA-Z0-9_]+)?"

    @contextmanager
    def _audio_stream(self, **kwargs) -> Generator[None, None, None]:
        response = send_request(
            'sound.record',
            dtype='int16',
            **kwargs,
        )

        assert response and not response.is_error(), (
            'Streaming error: ' + str(response.errors) if response else '(unknown)'
        )

        yield
        send_request('sound.stop_recording')

    @override
    @classmethod
    def _get_redis_queue(cls, *_, device: Optional[str] = None, **__) -> str:
        return '/'.join([cls._redis_queue_prefix, *([device] if device else [])])

    def _get_args(self, **kwargs):
        kwargs.update({k: v[0].decode() for k, v in self.request.arguments.items()})
        device = kwargs.get('device')
        return {
            'device': device,
            'sample_rate': int(kwargs.get('sample_rate', 44100)),
            'blocksize': int(kwargs.get('blocksize', 512)),
            'latency': float(kwargs.get('latency', 0)),
            'channels': int(kwargs.get('channels', 1)),
            'format': kwargs.get('format', 'wav'),
            'redis_queue': kwargs.get('redis_queue', self._get_redis_queue(device)),
        }

    @staticmethod
    def _content_type_by_extension(extension: str) -> str:
        if extension == 'mp3':
            return 'audio/mpeg'
        if extension == 'ogg':
            return 'audio/ogg'
        if extension == 'wav':
            return 'audio/wav;codec=pcm'
        if extension == 'flac':
            return 'audio/flac'
        if extension == 'aac':
            return 'audio/aac'
        return 'application/octet-stream'

    def get(self, extension: Optional[str] = None) -> None:
        ext = extension or 'wav'
        args = self._get_args(format=ext)

        try:
            with self._audio_stream(**args):
                self.set_header('Content-Type', self._content_type_by_extension(ext))
                self.forward_stream(**args)

            self.finish()
        except AssertionError as e:
            self.set_header("Content-Type", "application/json")
            self.set_status(400, str(e))
            self.finish(json.dumps({"error": str(e)}))
        except Exception as e:
            self.set_header("Content-Type", "application/json")
            self.logger.exception(e)
            self.set_status(500, str(e))
            self.finish(json.dumps({"error": str(e)}))
