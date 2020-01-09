from typing import Optional

from platypush.message import Mapping
from platypush.message.response import Response


class GoogleDriveResponse(Response):
    pass


class GoogleDriveFile(Mapping):
    # noinspection PyShadowingBuiltins
    def __init__(self,
                 type: str,
                 id: str,
                 name: str,
                 mime_type: Optional[str] = None,
                 *args, **kwargs):
        super().__init__(id=id, name=name, type=type,
                         mime_type=mime_type, *args, **kwargs)


# vim:sw=4:ts=4:et:
