from abc import ABC, abstractmethod
from typing import Optional

from .._config import XmppConfig
from ._base import XmppBaseMixin


# pylint: disable=too-few-public-methods
class XmppConfigMixin(XmppBaseMixin, ABC):
    """
    A simple mixin that encapsulates an XMPP configuration object.
    """

    @abstractmethod
    def __init__(self, *args, config: Optional[XmppConfig] = None, **kwargs):
        self._config = config or XmppConfig()
        super().__init__(*args, **kwargs)
