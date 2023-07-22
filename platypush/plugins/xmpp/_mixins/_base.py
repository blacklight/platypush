from abc import ABC, abstractmethod
from logging import getLogger
from typing import Optional, Union

import aioxmpp


# pylint: disable=too-few-public-methods
class XmppBaseMixin(ABC):
    """
    Base mixin for XMPP classes, containing common methods and properties.
    """

    DEFAULT_TIMEOUT = 20
    """Default timeout for async calls."""

    @abstractmethod
    def __init__(
        self,
        *_,
        user_id: Union[str, aioxmpp.JID],
        language: Optional[Union[str, aioxmpp.structs.LanguageTag]] = None,
        client: Optional[aioxmpp.Client] = None,
        **__,
    ):
        """
        :param user_id: Jabber/user ID, in the format ``user@example.org``.
        :param language: ISO string for the language code that will be used by
            the bot (default: ``None``).
        :param client: The main XMPP client.
        """
        self._jid = (
            aioxmpp.JID.fromstr(user_id) if isinstance(user_id, str) else user_id
        )
        """The client's registered JID."""
        self._lang = (
            aioxmpp.structs.LanguageTag.fromstr(language)
            if language and isinstance(language, str)
            else language
        )
        """The client's default language."""
        self._client: Optional[aioxmpp.Client] = client
        """The main XMPP client."""
        self.logger = getLogger(f'platypush:xmpp:{self.__class__.__name__}')

    @staticmethod
    def _jid_to_str(jid: aioxmpp.JID) -> str:
        """Convert a JID to a simple string in the format ``localpart@domain``."""
        return f'{jid.localpart}@{jid.domain}'
