import os
from typing import Optional, Union, Sequence

import requests
from requests.auth import HTTPBasicAuth

from platypush.plugins import action
from platypush.plugins.mail import MailOutPlugin


class MailgunPlugin(MailOutPlugin):
    """
    Mailgun integration.
    """
    def __init__(self, api_key: str, api_base_url: str = 'https://api.mailgun.net/v3', **kwargs):
        """
        :param api_key: Mailgun API secret key.
        :param api_base_url: Use ``https://api.eu.mailgun.net/v3`` if you are using an EU account.
        """
        super().__init__(**kwargs)
        self._api_key = api_key
        self._api_base_url = api_base_url

    def send_message(self, *_, **__):
        pass

    @action
    def send(
            self, domain: str, to: Union[str, Sequence[str]], from_: Optional[str] = None,
            cc: Optional[Union[str, Sequence[str]]] = None, bcc: Optional[Union[str, Sequence[str]]] = None,
            subject: str = '', body: str = '', body_type: str = 'plain', attachments: Optional[Sequence[str]] = None,
            **kwargs
     ):
        """
        Send an email through Mailgun.

        :param domain: From which registered domain the email(s) should be sent.
        :param to: Receiver(s), as comma-separated strings or list.
        :param from_: Sender email address (``from`` is also supported outside of Python contexts).
        :param cc: Carbon-copy addresses, as comma-separated strings or list
        :param bcc: Blind carbon-copy addresses, as comma-separated strings or list
        :param subject: Mail subject.
        :param body: Mail body.
        :param body_type: Mail body type - ``text`` or ``html``.
        :param attachments: List of attachment files to send.
        """
        from_ = from_ or kwargs.pop('from', None)
        rs = requests.post(
            f'{self._api_base_url}/{domain}/messages',
            auth=HTTPBasicAuth('api', self._api_key),
            data={
                'to': ', '.join([to] if isinstance(to, str) else to),
                'subject': subject,
                **{'html' if body_type == 'html' else 'text': body},
                **({'from': from_} if from_ else {}),
                **({'cc': ', '.join([cc] if isinstance(cc, str) else cc)} if cc else {}),
                **({'bcc': ', '.join([bcc] if isinstance(bcc, str) else bcc)} if bcc else {}),
            },
            files=[os.path.expanduser(attachment) for attachment in (attachments or [])]
        )

        rs.raise_for_status()


# vim:sw=4:ts=4:et:
