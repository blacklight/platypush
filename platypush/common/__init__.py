import inspect
import logging
import os
from typing import Any, Callable, Mapping, Sequence, Tuple

from platypush.utils.manifest import Manifest

from ._types import StoppableThread

logger = logging.getLogger('platypush')


def _build_args(
    func: Callable, *args, **kwargs
) -> Tuple[Sequence[Any], Mapping[str, Any]]:
    spec = inspect.getfullargspec(func)
    func_args = args if spec.varargs else args[: len(spec.args)]
    func_kwargs = (
        kwargs
        if spec.varkw
        else {
            arg: kwargs[arg] for arg in [*spec.args, *spec.kwonlyargs] if arg in kwargs
        }
    )

    return func_args, func_kwargs


def exec_wrapper(f: Callable[..., Any], *args, **kwargs):
    """
    Utility function that runs a callable with its arguments, wraps its
    response into a ``Response`` object and handles errors/exceptions.
    """
    from platypush import Response
    from platypush.plugins import register_action, unregister_action

    func_args, func_kwargs = _build_args(f, *args, **kwargs)
    action_name = f'{f.__module__}.{f.__name__}'

    if getattr(f, 'procedure', False):
        action_name = f'procedure:{getattr(f, "procedure_name", action_name)}'
    elif getattr(f, 'hook', False):
        action_name = f'event_hook:{action_name}'
    elif getattr(f, 'cron', False):
        action_name = f'cron:{action_name}'

    response = None
    action_id = register_action(
        {
            'action': action_name,
            'args': func_kwargs,
        }
    )

    try:
        ret = f(*func_args, **func_kwargs)
        if isinstance(ret, Response):
            return ret

        response = Response(output=ret)
        return response
    except Exception as e:
        logger.exception(e)
        response = Response(errors=[str(e)])
        return response
    finally:
        unregister_action(action_id, response=response)


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
