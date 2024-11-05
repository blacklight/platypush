from dataclasses import dataclass
from typing import IO

from ._base import MediaResource


@dataclass
class FileMediaResource(MediaResource):
    """
    Models a media resource that is read from a file.
    """

    def open(self, *args, **kwargs) -> IO:
        """
        Opens the media resource.
        """
        if self.fd is None:
            self.fd = open(self.resource, 'rb')  # pylint: disable=consider-using-with

        return super().open(*args, **kwargs)


# vim:sw=4:ts=4:et:
