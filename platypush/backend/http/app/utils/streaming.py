import logging
import os
import importlib
import inspect
from typing import List, Type

import pkgutil

from ..streaming import StreamingRoute

logger = logging.getLogger(__name__)


def get_streaming_routes() -> List[Type[StreamingRoute]]:
    """
    Scans for streaming routes.
    """
    from platypush.backend.http import HttpBackend

    base_pkg = '.'.join([HttpBackend.__module__, 'app', 'streaming'])
    base_dir = os.path.join(
        os.path.dirname(inspect.getfile(HttpBackend)), 'app', 'streaming'
    )
    routes = []

    for _, mod_name, _ in pkgutil.walk_packages([base_dir], prefix=base_pkg + '.'):
        try:
            module = importlib.import_module(mod_name)
        except Exception as e:
            logger.warning('Could not import module %s', mod_name)
            logger.exception(e)
            continue

        for _, obj in inspect.getmembers(module):
            if (
                inspect.isclass(obj)
                and not inspect.isabstract(obj)
                and issubclass(obj, StreamingRoute)
            ):
                routes.append(obj)

    return routes
