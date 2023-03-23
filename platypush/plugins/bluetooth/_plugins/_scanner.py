import importlib
import inspect
import logging
import os
import pkgutil
from typing import List

from platypush.plugins.bluetooth._plugins import BaseBluetoothPlugin

logger = logging.getLogger(__name__)


def scan_plugins(manager) -> List[BaseBluetoothPlugin]:
    """
    Initializes all the plugins associated to the given BluetoothManager by
    scanning all the modules under the ``_plugins`` folder in the manager's
    package.
    """
    plugins = {}
    base_dir = os.path.dirname(inspect.getfile(manager.__class__))
    module = inspect.getmodule(manager.__class__)
    assert module is not None
    package = module.__package__
    assert package is not None

    for _, mod_name, _ in pkgutil.walk_packages([base_dir], prefix=package + '.'):
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
                and issubclass(obj, BaseBluetoothPlugin)
            ):
                plugins[obj] = obj(manager)

    return list(plugins.values())
