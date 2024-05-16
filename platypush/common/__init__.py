import inspect
import logging
import os
from typing import Any, Callable

from platypush.utils.manifest import Manifest

from ._types import StoppableThread

logger = logging.getLogger('platypush')


def exec_wrapper(f: Callable[..., Any], *args, **kwargs):
    """
    Utility function that runs a callable with its arguments, wraps its
    response into a ``Response`` object and handles errors/exceptions.
    """
    from platypush import Response

    try:
        ret = f(*args, **kwargs)
        if isinstance(ret, Response):
            return ret

        return Response(output=ret)
    except Exception as e:
        logger.exception(e)
        return Response(errors=[str(e)])


# pylint: disable=too-few-public-methods
class ExtensionWithManifest:
    """
    This class models an extension with an associated manifest.json in the same
    folder.
    """

    def __init__(self, *_, **__):
        self._manifest = self.get_manifest()

    def get_manifest(self) -> Manifest:
        manifest_file = os.path.join(
            os.path.dirname(inspect.getfile(self.__class__)), 'manifest.json'
        )
        assert os.path.isfile(
            manifest_file
        ), f'The extension {self.__class__.__name__} has no associated manifest.json'

        return Manifest.from_file(manifest_file)


__all__ = [
    'ExtensionWithManifest',
    'StoppableThread',
    'exec_wrapper',
]
