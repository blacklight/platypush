import os
from typing import Optional

from ..._search.local.metadata import get_file_metadata
from .. import FileMediaResource
from ._base import MediaResourceParser


# pylint: disable=too-few-public-methods
class FileResourceParser(MediaResourceParser):
    """
    Parser for local file resources.
    """

    def parse(self, resource: str, *_, **__) -> Optional[FileMediaResource]:
        if resource.startswith('file://') or os.path.isfile(resource):
            path = resource
            if resource.startswith('file://'):
                path = resource[len('file://') :]

            assert os.path.isfile(path), f'File {path} not found'
            metadata = get_file_metadata(path)
            metadata['timestamp'] = metadata.pop('created_at', None)

            return FileMediaResource(
                resource=path,
                url=f'file://{path}',
                media_plugin=self._media,
                title=os.path.basename(resource),
                filename=os.path.basename(resource),
                **metadata,
            )

        return None


# vim:sw=4:ts=4:et:
