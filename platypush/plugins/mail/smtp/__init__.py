from contextlib import contextmanager
from email.message import Message
from typing import Dict, Generator

from smtplib import SMTP, SMTP_SSL

from .._model import TransportEncryption
from .._plugin import MailOutPlugin


class MailSmtpPlugin(MailOutPlugin):
    """
    Plugin to interact with a mail server over SMTP.
    """

    @classmethod
    def _matches_url_scheme(cls, scheme: str) -> bool:
        return scheme in ('smtp', 'smtps')

    @classmethod
    def default_ports(cls) -> Dict[TransportEncryption, int]:
        return {
            TransportEncryption.NONE: 25,
            TransportEncryption.SSL: 465,
            TransportEncryption.STARTTLS: 587,
        }

    @contextmanager
    def connect(self) -> Generator[SMTP, None, None]:
        smtp_args = {
            'host': self.server.server,
            'port': self.server.port,
        }

        if self.server.encryption == TransportEncryption.SSL:
            client_type = SMTP_SSL
            if self.server.certfile:
                smtp_args.update(certfile=self.server.certfile)
            if self.server.keyfile:
                smtp_args.update(keyfile=self.server.keyfile)
        else:
            client_type = SMTP

        client = client_type(**smtp_args)

        if self.server.encryption == TransportEncryption.STARTTLS:
            client.ehlo()
            client.starttls()
        else:
            client.ehlo_or_helo_if_needed()

        pwd = None
        try:
            pwd = self.account.get_password()
        except AssertionError:
            pass

        if pwd:
            client.login(self.account.username, pwd)

        yield client
        client.quit()

    def send_message(self, message: Message, **_):
        with self.connect() as client:
            errors = client.sendmail(
                message['From'], message['To'], message.as_string()
            )

        assert not errors, 'Failed to send message: ' + str(
            [f'{code}: {err}' for code, err in errors.items()]
        )


# vim:sw=4:ts=4:et:
