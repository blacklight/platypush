from dataclasses import dataclass

from ._base import MediaResource


@dataclass
class HttpMediaResource(MediaResource):
    """
    Models a media resource that is read from an HTTP response.
    """

    def open(self, *args, **kwargs):
        return super().open(*args, **kwargs)

    def close(self) -> None:
        super().close()


# vim:sw=4:ts=4:et:
