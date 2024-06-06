"""
Platypush

.. moduleauthor:: Fabio Manganiello <fabio@manganiello.tech>
.. license: MIT
"""

from .app import Application, app
from .config import Config
from .context import Variable, get_backend, get_bus, get_plugin
from .cron import cron
from .event.hook import hook
from .message.event import Event
from .message.request import Request
from .message.response import Response
from .procedure import procedure
from .runner import main
from .utils import run

# Alias for platypush.event.hook.hook,
# see https://git.platypush.tech/platypush/platypush/issues/399
when = hook


__author__ = 'Fabio Manganiello <fabio@manganiello.tech>'
__version__ = '1.1.0'
__all__ = [
    'Application',
    'Variable',
    'Config',
    'Event',
    'Request',
    'Response',
    'app',
    'cron',
    'get_backend',
    'get_bus',
    'get_plugin',
    'hook',
    'main',
    'procedure',
    'run',
    'when',
]


# vim:sw=4:ts=4:et:
