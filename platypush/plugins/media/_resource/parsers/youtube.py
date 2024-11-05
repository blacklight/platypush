import inspect
import json
import re
import subprocess
from dataclasses import fields
from typing import Dict, Optional

from .. import YoutubeMediaResource
from ._base import MediaResourceParser


class YoutubeResourceParser(MediaResourceParser):
    """
    Parser for yt-dlp-compatible resources.
    """

    @staticmethod
    def _get_extractors():
        try:
            from yt_dlp.extractor import _extractors  # type: ignore
        except ImportError:
            # yt-dlp not installed
            return

        for _, obj_type in inspect.getmembers(_extractors):
            if (
                inspect.isclass(obj_type)
                and isinstance(getattr(obj_type, "_VALID_URL", None), str)
                and obj_type.__name__ != "GenericIE"
            ):
                yield obj_type

    @classmethod
    def is_youtube_resource(cls, resource: str):
        return any(
            re.search(getattr(extractor, '_VALID_URL', '^$'), resource)
            for extractor in cls._get_extractors()
        )

    @staticmethod
    def _get_youtube_best_thumbnail(info: Dict[str, dict]):
        thumbnails = info.get('thumbnails', {})
        if not thumbnails:
            return None

        # Preferred resolution
        for res in ((640, 480), (480, 360), (320, 240)):
            thumb = next(
                (
                    thumb
                    for thumb in thumbnails
                    if thumb.get('width') == res[0] and thumb.get('height') == res[1]
                ),
                None,
            )

            if thumb:
                return thumb.get('url')

        # Default fallback (best quality)
        return info.get('thumbnail')

    def parse(
        self,
        resource: str,
        *_,
        youtube_format: Optional[str] = None,
        youtube_audio_format: Optional[str] = None,
        only_audio: bool = False,
        **__
    ) -> Optional[YoutubeMediaResource]:
        if not self.is_youtube_resource(resource):
            return None

        youtube_format = youtube_format or self._media.youtube_format
        if only_audio:
            youtube_format = (
                youtube_audio_format
                or self._media.youtube_audio_format
                or youtube_format
            )

        ytdl_cmd = [
            self._media._ytdl,  # pylint: disable=protected-access
            *(['-f', youtube_format] if youtube_format else []),
            *(['-x'] if only_audio else []),
            '-j',
            '-g',
            resource,
        ]

        self.logger.info('Executing command %s', ' '.join(ytdl_cmd))
        with subprocess.Popen(ytdl_cmd, stdout=subprocess.PIPE) as ytdl:
            output = ytdl.communicate()[0].decode().strip()
            ytdl.wait()

        self.logger.debug('yt-dlp output: %s', output)
        lines = output.split('\n')

        if not lines:
            self.logger.warning('No output from yt-dlp')
            return None

        info = json.loads(lines[-1])
        args = {
            **{
                field.name: info.get(field.name)
                for field in fields(YoutubeMediaResource)
            },
            'url': info.get('webpage_url'),
            'image': self._get_youtube_best_thumbnail(info),
            'type': info.get('extractor'),
            'media_plugin': self._media,
        }

        return YoutubeMediaResource(**args)


# vim:sw=4:ts=4:et:
