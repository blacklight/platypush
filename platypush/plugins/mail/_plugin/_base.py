import logging
import os
import re

from abc import ABC, abstractmethod
from typing import Dict, Optional
from urllib.parse import urlparse

from .._model import AccountConfig, ServerConfig, TransportEncryption

email_match_re = re.compile(r'[^@]+@[^@]+\.[^@]+')


class BaseMailPlugin(ABC):  # pylint: disable=too-few-public-methods
    """
    Base class for mail plugins.
    """

    def __init__(
        self,
        server: str,
        account: AccountConfig,
        timeout: float,
        keyfile: Optional[str] = None,
        certfile: Optional[str] = None,
        domain: Optional[str] = None,
        **_,
    ):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.account = account
        self.server = self._get_server_config(
            server=server,
            timeout=timeout,
            keyfile=keyfile,
            certfile=certfile,
            domain=domain,
        )

    @staticmethod
    def _get_path(path: str) -> str:
        return os.path.abspath(os.path.expanduser(path))

    @classmethod
    def _get_server_config(
        cls,
        server: str,
        timeout: float,
        keyfile: Optional[str],
        certfile: Optional[str],
        domain: Optional[str],
    ) -> ServerConfig:
        url = urlparse(server)
        assert url.hostname, f'No hostname specified: "{server}"'

        ssl = TransportEncryption.by_url_scheme(url.scheme)
        port = url.port or cls.default_ports().get(ssl)
        assert port, f'No port specified and no default available: "{server}"'

        if keyfile:
            keyfile = cls._get_path(keyfile)
        if certfile:
            certfile = cls._get_path(certfile)

        return ServerConfig(
            server=url.hostname,
            port=port,
            encryption=ssl,
            timeout=timeout,
            keyfile=keyfile,
            certfile=certfile,
            domain=domain,
        )

    @property
    def from_string(self):
        """
        :return: The from string for the account.
        """
        return self.account.display_name or self.account.username

    @classmethod
    @abstractmethod
    def _matches_url_scheme(cls, scheme: str) -> bool:
        raise NotImplementedError()

    @classmethod
    def can_handle(cls, url: str) -> bool:
        """
        Check whether the plugin can handle the specified URL.
        """
        return cls._matches_url_scheme(urlparse(url).scheme)

    @classmethod
    @abstractmethod
    def default_ports(cls) -> Dict[TransportEncryption, int]:
        """
        :return: A mapping of transport encryption to default port.
        """
        raise NotImplementedError()

    @classmethod
    def build(
        cls,
        server: str,
        account: AccountConfig,
        timeout: float,
        keyfile: Optional[str] = None,
        certfile: Optional[str] = None,
    ) -> 'BaseMailPlugin':
        from ._utils import mail_plugins

        url_parsed = urlparse(server)
        assert url_parsed.hostname, f'No hostname specified: "{server}"'

        mail_cls = next(
            (plugin for plugin in mail_plugins if plugin.can_handle(server)),
            None,
        )

        assert mail_cls, f'No mail plugin found for URL: "{server}"'
        return mail_cls(
            server=server,
            account=account,
            timeout=timeout,
            keyfile=keyfile,
            certfile=certfile,
        )


# vim:sw=4:ts=4:et:
