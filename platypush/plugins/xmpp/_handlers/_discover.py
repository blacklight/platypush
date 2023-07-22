import importlib
import inspect
import os
from typing import List, Type

import pkgutil

from ._base import XmppBaseHandler


def discover_handlers() -> List[Type[XmppBaseHandler]]:
    """
    Discover the handler classes defined in this module.
    """

    base_pkg = '.'.join(__name__.split('.')[:-1])
    base_dir = os.path.dirname(__file__)
    return [
        obj
        for _, mod_name, _ in pkgutil.walk_packages([base_dir], prefix=base_pkg + '.')
        for _, obj in inspect.getmembers(importlib.import_module(mod_name))
        if inspect.isclass(obj)
        and not inspect.isabstract(obj)
        and issubclass(obj, XmppBaseHandler)
    ]
