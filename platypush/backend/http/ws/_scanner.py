import os
import importlib
import inspect
from typing import List, Type

import pkgutil

from ._base import WSRoute, logger


def scan_routes() -> List[Type[WSRoute]]:
    """
    Scans for websocket route objects.
    """

    base_dir = os.path.dirname(__file__)
    routes = []

    for _, mod_name, _ in pkgutil.walk_packages([base_dir], prefix=__package__ + '.'):
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
                and issubclass(obj, WSRoute)
            ):
                routes.append(obj)

    return routes
