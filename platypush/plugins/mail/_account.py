from dataclasses import dataclass
from typing import Any, Collection, Dict, Optional

from ._model import AccountConfig
from ._plugin import BaseMailPlugin, MailInPlugin, MailOutPlugin


@dataclass
class Account:
    """
    Models a mail account.
    """

    name: str
    poll_interval: float
    display_name: Optional[str] = None
    incoming: Optional[MailInPlugin] = None
    outgoing: Optional[MailOutPlugin] = None
    monitor_folders: Optional[Collection[str]] = None
    default: bool = False
    last_check: Optional[float] = None

    @classmethod
    def build(
        cls,
        name: str,
        timeout: float,
        poll_interval: float,
        display_name: Optional[str] = None,
        incoming: Optional[Dict[str, Any]] = None,
        outgoing: Optional[Dict[str, Any]] = None,
        monitor_folders: Optional[Collection[str]] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        password_cmd: Optional[str] = None,
        keyfile: Optional[str] = None,
        certfile: Optional[str] = None,
        access_token: Optional[str] = None,
        oauth_mechanism: Optional[str] = None,
        oauth_vendor: Optional[str] = None,
        default: bool = False,
        last_check: Optional[float] = None,
    ) -> 'Account':
        account_args = {
            'username': username,
            'password': password,
            'password_cmd': password_cmd,
            'access_token': access_token,
            'oauth_mechanism': oauth_mechanism,
            'oauth_vendor': oauth_vendor,
            'display_name': display_name,
        }

        in_plugin = None
        if incoming:
            server = incoming.pop('server', None)
            assert server, 'No server provided for incoming mail for account "{name}"'

            keyfile = incoming.pop('keyfile', keyfile)
            certfile = incoming.pop('certfile', certfile)
            account = AccountConfig(**{**account_args, **incoming})
            in_plugin = BaseMailPlugin.build(
                server=server,
                account=account,
                timeout=timeout,
                keyfile=keyfile,
                certfile=certfile,
            )

            assert isinstance(
                in_plugin, MailInPlugin
            ), 'Incoming mail plugin expected for account "{name}"'

        out_plugin = None
        if outgoing:
            server = outgoing.pop('server', None)
            assert server, 'No server provided for outgoing mail for account "{name}"'

            keyfile = outgoing.pop('keyfile', keyfile)
            certfile = outgoing.pop('certfile', certfile)
            account = AccountConfig(**{**account_args, **outgoing})
            out_plugin = BaseMailPlugin.build(
                server=server,
                account=account,
                timeout=timeout,
                keyfile=keyfile,
                certfile=certfile,
            )

            assert isinstance(
                out_plugin, MailOutPlugin
            ), 'Outgoing mail plugin expected for account "{name}"'

        return cls(
            name=name,
            display_name=display_name,
            incoming=in_plugin,
            outgoing=out_plugin,
            monitor_folders=monitor_folders,
            poll_interval=poll_interval,
            default=default,
            last_check=last_check,
        )


# vim:sw=4:ts=4:et:
