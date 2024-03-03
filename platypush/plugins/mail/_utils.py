import re
from typing import Optional
from urllib.parse import urlparse

from dns.exception import DNSException
from dns.resolver import resolve

from ._account import AccountConfig
from ._model import ServerConfig

_email_regex = re.compile(r'[^@]+@[^@]+\.[^@]+')
_from_header_regex = re.compile(r'^(?:"?([^"]+)"?\s+)?<?([^>]+)>?$')
_ipv4_regex = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
_ipv6_regex = re.compile(r'^[0-9a-fA-F:]+$')


def infer_mail_domain(account: AccountConfig, server: ServerConfig) -> str:
    """
    Infers the mail domain from the account and server configuration.
    """

    if server.domain:
        return server.domain

    if account.username and _email_regex.match(account.username):
        return account.username.split('@', 1)[1]

    if server.server:
        if _ipv4_regex.match(server.server) or _ipv6_regex.match(server.server):
            return server.server

        host = urlparse(server.server).hostname
        assert host, f'Could not parse hostname from server URL: {server.server}'
        host_tokens = host.split('.')

        while host_tokens:
            try:
                resolve(host, 'MX')
                return host
            except DNSException:
                host_tokens.pop(0)
                host = '.'.join(host_tokens)

        raise AssertionError(f'Could not resolve MX record for {host}')

    raise AssertionError('Could not infer mail domain from configuration.')


def infer_mail_address(account: AccountConfig, server: ServerConfig) -> str:
    if account.username and _email_regex.match(account.username):
        return account.username

    return f'{account.username}@{infer_mail_domain(account, server)}'


def normalize_from_header(
    from_: Optional[str], account: AccountConfig, server: ServerConfig
) -> str:
    """
    Normalizes the value of the "From" header.
    """

    if not from_:
        from_ = account.display_name or account.username

    if _email_regex.match(from_):
        return from_

    m = _from_header_regex.match(from_)
    if m and _email_regex.match(m.group(2)):
        return f'{m.group(1)} <{m.group(2)}>'

    return f'{from_} <{infer_mail_address(account, server)}>'
