import importlib
import inspect
import os

from threading import RLock
from typing import Set, Type

import pkgutil

from ._base import BaseMailPlugin


def _scan_mail_plugins() -> Set[Type[BaseMailPlugin]]:
    from platypush.plugins import mail

    # Recursively scan for class inside the `mail` module that inherit from
    # BaseMailPlugin
    base_file = inspect.getfile(mail)
    plugins = set()

    for _, name, _ in pkgutil.walk_packages(
        [os.path.dirname(base_file)], prefix=f'{mail.__name__}.'
    ):
        module = importlib.import_module(name)
        for _, cls in inspect.getmembers(module, inspect.isclass):
            if not inspect.isabstract(cls) and issubclass(cls, BaseMailPlugin):
                plugins.add(cls)

    return plugins


_mail_plugins_lock = RLock()
mail_plugins = set()

with _mail_plugins_lock:
    if not mail_plugins:
        mail_plugins = _scan_mail_plugins()


# vim:sw=4:ts=4:et:
