from abc import ABC, abstractmethod

import aioxmpp

from .._mixins import XmppAsyncMixin, XmppConfigMixin, XmppEventStateMixin


# pylint: disable=too-few-public-methods
class XmppBaseHandler(XmppAsyncMixin, XmppConfigMixin, XmppEventStateMixin, ABC):
    """
    Base class for XMPP handlers.
    """

    _client: aioxmpp.Client

    @abstractmethod
    def __init__(self, *args, **kwargs):
        """
        To be implemented by the subclasses.
        """
        super().__init__(*args, **kwargs)
