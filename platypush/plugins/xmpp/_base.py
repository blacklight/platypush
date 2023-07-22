from abc import ABC, abstractmethod
from typing import Type

from ._mixins import XmppAsyncMixin, XmppBaseMixin, XmppConfigMixin, XmppEventStateMixin


class XmppBasePlugin(XmppAsyncMixin, XmppConfigMixin, XmppEventStateMixin, ABC):
    """
    Base interface for the XMPP plugin.
    """

    @abstractmethod
    def register_handler(self, hndl_type: Type[XmppBaseMixin]):
        raise NotImplementedError
