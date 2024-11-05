import os
from typing import Optional

from .. import HttpMediaResource
from ._base import MediaResourceParser


# pylint: disable=too-few-public-methods
class HttpResourceParser(MediaResourceParser):
    """
    Parser for HTTP resources.
    """

    def parse(self, resource: str, *_, **__) -> Optional[HttpMediaResource]:
        if resource.startswith('http://') or resource.startswith('https://'):
            assert self._media.is_media_file(
                resource
            ), f'Invalid media resource: {resource}'

            return HttpMediaResource(
                resource=resource,
                url=resource,
                media_plugin=self._media,
                title=os.path.basename(resource),
                filename=os.path.basename(resource),
            )

        return None


# vim:sw=4:ts=4:et:
