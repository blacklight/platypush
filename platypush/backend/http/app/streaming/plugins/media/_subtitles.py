import json

from tornado.web import stream_request_body

from platypush.backend.http.app.streaming import StreamingRoute
from platypush.backend.http.app.utils.bus import send_request

from ._registry import load_media_map


@stream_request_body
class MediaSubtitlesRoute(StreamingRoute):
    """
    Route for media stream subtitles.
    """

    SUPPORTED_METHODS = ['GET', 'POST', 'DELETE']

    @classmethod
    def path(cls) -> str:
        return r"^/media/subtitles/([a-zA-Z0-9_.]+)\.vtt$"

    @property
    def auth_required(self) -> bool:
        return False

    def get(self, media_id: str):
        """
        GET route to retrieve the subtitles for the given media_id.
        """
        try:
            self.get_subtitles(media_id)
        except Exception as e:
            self._on_error(e)

    def post(self, media_id: str):
        """
        POST route to add subtitles to the given media_id.
        """
        try:
            self.add_subtitles(media_id)
        except Exception as e:
            self._on_error(e)

    def delete(self, media_id: str):
        """
        DELETE route to remove the subtitles for the given media_id.
        """
        try:
            self.remove_subtitles(media_id)
        except Exception as e:
            self._on_error(e)

    def get_subtitles(self, media_id: str):
        """
        Retrieves the subtitles for the given media_id.
        """

        media_hndl = load_media_map().get(media_id)
        if not media_hndl:
            raise FileNotFoundError(f'{media_id} is not a registered media_id')

        if not media_hndl.subtitles:
            raise FileNotFoundError(f'{media_id} has no subtitles')

        with open(media_hndl.subtitles) as f:
            self.set_header('Content-Type', 'text/vtt')
            self.finish(f.read())

    @staticmethod
    def remove_subtitles(media_id: str):
        """
        Remove the current subtitle track from a streamed from a media file.
        """
        media_hndl = load_media_map().get(media_id)
        if not media_hndl:
            raise FileNotFoundError(f'{media_id} is not a registered media_id')

        if not media_hndl.subtitles:
            raise FileNotFoundError(f'{media_id} has no subtitles attached')

        media_hndl.remove_subtitles()
        return {}

    def add_subtitles(self, media_id: str):
        """
        This route can be used to download and/or expose subtitles files
        associated to a media file
        """

        media_hndl = load_media_map().get(media_id)
        if not media_hndl:
            raise FileNotFoundError(f'{media_id} is not a registered media_id')

        subfile = None
        if self.request.body:
            subfile = json.loads(self.request.body).get('filename')
            assert subfile, 'No filename specified in the request'

        if not subfile:
            if not media_hndl.path:
                raise NotImplementedError(
                    'Subtitles are currently only supported for local media files'
                )

            req = {
                'type': 'request',
                'action': 'media.subtitles.get_subtitles',
                'args': {
                    'resource': media_hndl.path,
                },
            }

            try:
                subtitles = send_request(req) or []
            except Exception as e:
                raise RuntimeError(f'Could not get subtitles: {e}') from e

            if not subtitles:
                raise FileNotFoundError(
                    f'No subtitles found for resource {media_hndl.path}'
                )

            req = {
                'type': 'request',
                'action': 'media.subtitles.download',
                'args': {
                    'link': subtitles[0].get('SubDownloadLink'),
                    'media_resource': media_hndl.path,
                    'convert_to_vtt': True,
                },
            }

            subfile = (send_request(req) or {}).get('filename')

        media_hndl.set_subtitles(subfile)
        return {
            'filename': subfile,
            'url': f'/media/subtitles/{media_id}.vtt',
        }
