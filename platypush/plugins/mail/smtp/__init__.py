from email.message import Message
from typing import Optional, List

from smtplib import SMTP, SMTP_SSL

from platypush.plugins.mail import MailOutPlugin, ServerInfo


class MailSmtpPlugin(MailOutPlugin):
    """
    Plugin to interact with a mail server over SMTP.
    """

    _default_port = 25
    _default_ssl_port = 465

    def __init__(self, server: Optional[str] = None, port: Optional[int] = None, local_hostname: Optional[str] = None,
                 source_address: Optional[List[str]] = None, username: Optional[str] = None,
                 password: Optional[str] = None, password_cmd: Optional[str] = None, access_token: Optional[str] = None,
                 oauth_mechanism: Optional[str] = 'XOAUTH2', oauth_vendor: Optional[str] = None, ssl: bool = False,
                 keyfile: Optional[str] = None, certfile: Optional[str] = None, timeout: Optional[int] = 60, **kwargs):
        """
        :param server: Server name/address.
        :param port: Port (default: 25 for plain, 465 for SSL).
        :param local_hostname: If specified, local_hostname is used as the FQDN of the local host in the HELO/EHLO
            command. Otherwise, the local hostname is found using socket.getfqdn().
        :param source_address:  The optional source_address parameter allows binding to some specific source address in
            a machine with multiple network interfaces, and/or to some specific source TCP port. It takes a 2-tuple
            (host, port), for the socket to bind to as its source address before connecting. If omitted (or if host or
            port are '' and/or 0 respectively) the OS default behavior will be used.
        :param username: SMTP username.
        :param password: SMTP password.
        :param password_cmd: If you don't want to input your password in the configuration, run this command to fetch
            or decrypt the password.
        :param access_token: OAuth2 access token if the server supports OAuth authentication.
        :param oauth_mechanism: OAuth2 mechanism (default: ``XOAUTH2``).
        :param oauth_vendor: OAuth2 vendor (default: None).
        :param ssl: Use SSL (default: False).
        :param keyfile: Private key file for SSL connection if client authentication is required.
        :param certfile: SSL certificate file or chain.
        :param timeout: Server connect/read timeout in seconds (default: 60).
        """
        super().__init__(**kwargs)
        self.local_hostname = local_hostname
        self.source_address = source_address
        self.server_info = self._get_server_info(server=server, port=port, username=username, password=password,
                                                 password_cmd=password_cmd, ssl=ssl, keyfile=keyfile, certfile=certfile,
                                                 access_token=access_token, oauth_mechanism=oauth_mechanism,
                                                 oauth_vendor=oauth_vendor, timeout=timeout)

    def _get_server_info(self, server: Optional[str] = None, port: Optional[int] = None, username: Optional[str] = None,
                         password: Optional[str] = None, password_cmd: Optional[str] = None,
                         ssl: Optional[bool] = None, keyfile: Optional[str] = None, certfile: Optional[str] = None,
                         timeout: Optional[int] = None, **kwargs) -> ServerInfo:
        return super()._get_server_info(server=server, port=port, username=username, password=password,
                                        password_cmd=password_cmd, ssl=ssl, keyfile=keyfile, certfile=certfile,
                                        default_port=self._default_port, default_ssl_port=self._default_ssl_port,
                                        timeout=timeout)

    def connect(self, **connect_args) -> SMTP:
        info = self._get_server_info(**connect_args)
        self.logger.info('Connecting to {}'.format(info.server))
        smtp_args = {
            'host': info.server,
            'port': info.port,
            'local_hostname': self.local_hostname,
            'source_address': self.source_address,
        }

        if info.ssl:
            client_type = SMTP_SSL
            smtp_args.update(certfile=info.certfile, keyfile=info.keyfile)
        else:
            client_type = SMTP

        client = client_type(**smtp_args)
        if info.password:
            client.login(info.username, info.password)

        return client

    def send_message(self, message: Message, **connect_args):
        with self.connect(**connect_args) as client:
            errors = client.sendmail(message['From'], message['To'], message.as_string())

        if errors:
            return None, ['{}: {}'.format(code, err) for code, err in errors.items()]


# vim:sw=4:ts=4:et:
