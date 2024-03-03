from typing import Optional, Union, Sequence

import requests
from requests.auth import HTTPBasicAuth

from platypush.plugins import Plugin, action


class MailgunPlugin(Plugin):
    """
    Mailgun integration.
    """

    def __init__(
        self,
        api_key: str,
        api_base_url: str = 'https://api.mailgun.net/v3',
        domain: Optional[str] = None,
        timeout: float = 20.0,
        **kwargs,
    ):
        """
        :param api_key: Mailgun API secret key.
        :param api_base_url: Use ``https://api.eu.mailgun.net/v3`` if you are using an EU account.
        :param domain: Default registered domain that should be used for sending
            emails if not specified in the :meth:`.send` action.
        :param timeout: Default timeout for the requests (default: 20 seconds).
        """
        super().__init__(**kwargs)
        self._api_key = api_key
        self._api_base_url = api_base_url
        self._domain = domain
        self._timeout = timeout

    @action
    def send(
        self,
        to: Union[str, Sequence[str]],
        from_: Optional[str] = None,
        cc: Optional[Union[str, Sequence[str]]] = None,
        bcc: Optional[Union[str, Sequence[str]]] = None,
        subject: str = '',
        body: str = '',
        body_type: str = 'plain',
        domain: Optional[str] = None,
        **kwargs,
    ):
        """
        Send an email through Mailgun.

        :param domain: From which registered domain the email(s) should be sent
            (default: the domain specified in the plugin configuration).
        :param to: Receiver(s), as comma-separated strings or list.
        :param from_: Sender email address (``from`` is also supported outside of Python contexts).
        :param cc: Carbon-copy addresses, as comma-separated strings or list
        :param bcc: Blind carbon-copy addresses, as comma-separated strings or list
        :param subject: Mail subject.
        :param body: Mail body.
        :param body_type: Mail body type - ``text`` or ``html``.
        """
        domain = domain or self._domain
        assert domain, 'No domain specified'
        from_ = from_ or kwargs.pop('from', None)
        rs = requests.post(
            f'{self._api_base_url}/{domain}/messages',
            timeout=self._timeout,
            auth=HTTPBasicAuth('api', self._api_key),
            data={
                'to': ', '.join([to] if isinstance(to, str) else to),
                'subject': subject,
                **{'html' if body_type == 'html' else 'text': body},
                **({'from': from_} if from_ else {}),
                **(
                    {'cc': ', '.join([cc] if isinstance(cc, str) else cc)} if cc else {}
                ),
                **(
                    {'bcc': ', '.join([bcc] if isinstance(bcc, str) else bcc)}
                    if bcc
                    else {}
                ),
            },
        )

        rs.raise_for_status()


# vim:sw=4:ts=4:et:
