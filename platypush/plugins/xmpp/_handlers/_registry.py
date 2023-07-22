from collections import defaultdict
from typing import Type
from typing_extensions import override

from .._base import XmppBasePlugin
from ._base import XmppBaseHandler


class XmppHandlersRegistry(defaultdict):
    """
    A registry of the initialized XMPP handlers.
    """

    def __init__(self, plugin: XmppBasePlugin):
        super().__init__()
        self._plugin = plugin

    @override
    def __missing__(self, hndl_type: Type[XmppBaseHandler]) -> XmppBaseHandler:
        return self._plugin.register_handler(hndl_type)
