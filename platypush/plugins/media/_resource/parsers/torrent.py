import os
import queue
from typing import Optional

from platypush.context import get_plugin

from .. import FileMediaResource
from ._base import MediaResourceParser


# pylint: disable=too-few-public-methods
class TorrentResourceParser(MediaResourceParser):
    """
    Parser for magnet links.
    """

    @staticmethod
    def _torrent_event_handler(evt_queue):
        def handler(event):
            # More than 5% of the torrent has been downloaded
            if event.args.get('progress', 0) > 5 and event.args.get('files'):
                evt_queue.put(
                    [f for f in event.args['files'] if f.is_media_file(f.filename)]
                )

        return handler

    def parse(self, resource: str, *_, **__) -> Optional[FileMediaResource]:
        if not resource.startswith('magnet:?'):
            return None

        torrents = get_plugin(self._media.torrent_plugin)
        assert torrents, f'{self._media.torrent_plugin} plugin not configured'

        evt_queue = queue.Queue()
        torrents.download(
            resource,
            download_dir=self._media.download_dir,
            _async=True,
            is_media=True,
            event_hndl=self._torrent_event_handler(evt_queue),
        )

        resources = [f for f in evt_queue.get()]  # noqa: C416,R1721

        if resources:
            self._media._videos_queue = videos_queue = sorted(resources)
            resource = videos_queue.pop(0)
        else:
            raise RuntimeError(f'No media file found in torrent {resource}')

        assert resource, 'Unable to find any compatible media resource'
        return FileMediaResource(
            resource=resource,
            url=f'file://{resource}',
            media_plugin=self._media,
            title=os.path.basename(resource),
            filename=os.path.basename(resource),
        )


# vim:sw=4:ts=4:et:
