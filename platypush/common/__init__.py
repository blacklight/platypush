import inspect
import logging
import os

from platypush.utils.manifest import Manifest

from ._types import StoppableThread

logger = logging.getLogger('platypush')


def exec_wrapper(f, *args, **kwargs):
    from platypush import Response

    try:
        ret = f(*args, **kwargs)
        if isinstance(ret, Response):
            return ret

        return Response(output=ret)
    except Exception as e:
        logger.exception(e)
        return Response(errors=[str(e)])


class ExtensionWithManifest:
    def __init__(self, *_, **__):
        self._manifest = self.get_manifest()

    def get_manifest(self) -> Manifest:
        manifest_file = os.path.join(
            os.path.dirname(inspect.getfile(self.__class__)), 'manifest.yaml'
        )
        assert os.path.isfile(
            manifest_file
        ), 'The extension {} has no associated manifest.yaml'.format(
            self.__class__.__name__
        )

        return Manifest.from_file(manifest_file)


__all__ = [
    'ExtensionWithManifest',
    'StoppableThread',
    'exec_wrapper',
]
