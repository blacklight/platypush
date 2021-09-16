import inspect
import os
import subprocess

from dataclasses import dataclass
from datetime import datetime
from email.message import Message
from email.mime.application import MIMEApplication
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from mimetypes import guess_type
from typing import Optional, List, Union, Any, Dict

from platypush.message import JSONAble
from platypush.plugins import Plugin, action


@dataclass
class ServerInfo:
    server: str
    port: int
    username: Optional[str]
    password: Optional[str]
    ssl: bool
    keyfile: Optional[str]
    certfile: Optional[str]
    access_token: Optional[str]
    oauth_mechanism: Optional[str]
    oauth_vendor: Optional[str]
    timeout: Optional[int]


class Mail(JSONAble):
    def __init__(self, id: int, date: datetime, size: int,
                 from_: Optional[Union[Dict[str, str], List[str]]] = None,
                 to: Optional[Union[Dict[str, str], List[str]]] = None,
                 cc: Optional[Union[Dict[str, str], List[str]]] = None,
                 bcc: Optional[Union[Dict[str, str], List[str]]] = None, subject: str = '',
                 payload: Optional[Any] = None, **kwargs):
        self.id = id
        self.date = date
        self.size = size
        self.from_ = from_ or kwargs.get('from')
        self.to = to
        self.cc = cc or []
        self.bcc = bcc or []
        self.subject = subject
        self.payload = payload

        for k, v in kwargs.items():
            setattr(self, k, v)

    def to_json(self) -> dict:
        return {
            k if k != 'from_' else 'from': v
            for k, v in dict(inspect.getmembers(self)).items()
            if not k.startswith('_') and not callable(v)
        }


class MailPlugin(Plugin):
    """
    Base class for mail plugins.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.server_info: Optional[ServerInfo] = None

    @staticmethod
    def _get_password(password: Optional[str] = None, password_cmd: Optional[str] = None) -> Optional[str]:
        """
        Get the password either from a provided string or from a password command.
        """
        if not password_cmd:
            return password

        proc = subprocess.Popen(['sh', '-c', password_cmd], stdout=subprocess.PIPE)
        password = proc.communicate()[0].decode()
        return password or None

    @staticmethod
    def _get_path(path: str) -> str:
        return os.path.abspath(os.path.expanduser(path))

    def _get_server_info(self, server: Optional[str] = None, port: Optional[int] = None, username: Optional[str] = None,
                         password: Optional[str] = None, password_cmd: Optional[str] = None,
                         ssl: Optional[bool] = None, keyfile: Optional[str] = None, certfile: Optional[str] = None,
                         access_token: Optional[str] = None, oauth_mechanism: Optional[str] = None,
                         oauth_vendor: Optional[str] = None, default_port: Optional[int] = None,
                         default_ssl_port: Optional[int] = None, timeout: Optional[int] = None, **kwargs) \
            -> ServerInfo:
        if not port:
            port = default_ssl_port if ssl else default_port

        info = ServerInfo(server=server, port=port, username=username,
                          password=self._get_password(password, password_cmd), ssl=ssl, keyfile=keyfile,
                          certfile=certfile, access_token=access_token, oauth_mechanism=oauth_mechanism,
                          oauth_vendor=oauth_vendor, timeout=timeout)

        if server:
            return info

        if self.server_info:
            assert self.server_info.server, 'No server specified'
            return self.server_info

        return info


class MailInPlugin(MailPlugin):
    """
    Base class for mail in plugins.
    """

    @action
    def get_folders(self) -> list:
        raise NotImplementedError()

    @action
    def get_sub_folders(self) -> list:
        raise NotImplementedError()

    @action
    def search(self, criteria: str, directory: Optional[str] = None) -> list:
        raise NotImplementedError()

    @action
    def search_unseen_messages(self, directory: Optional[str] = None) -> list:
        raise NotImplementedError()

    def search_flagged_messages(self, folder: str = 'INBOX', **connect_args) -> list:
        raise NotImplementedError()

    @action
    def get_message(self, id) -> dict:
        raise NotImplementedError()


class MailOutPlugin(MailPlugin):
    """
    Base class for mail out plugins.
    """

    def send_message(self, message: Message, **connect_args):
        raise NotImplementedError()

    @staticmethod
    def _file_to_part(file: str) -> MIMEBase:
        _type, _subtype, _type_class = 'application', 'octet-stream', MIMEApplication
        mime_type, _sub_subtype = guess_type(file)

        if mime_type:
            _type, _subtype = mime_type.split('/')
        if _sub_subtype:
            _subtype += ';' + _sub_subtype

        if _type == 'application':
            _type_class = MIMEApplication
        elif _type == 'audio':
            _type_class = MIMEAudio
        elif _type == 'image':
            _type_class = MIMEImage
        elif _type == 'text':
            _type_class = MIMEText

        args = {}
        if _type_class != MIMEText:
            mode = 'rb'
            args['Name'] = os.path.basename(file)
        else:
            mode = 'r'

        with open(file, mode) as f:
            return _type_class(f.read(), _subtype, **args)

    @classmethod
    def create_message(cls, to: Union[str, List[str]], from_: Optional[str] = None,
                       cc: Optional[Union[str, List[str]]] = None, bcc: Optional[Union[str, List[str]]] = None,
                       subject: str = '', body: str = '', body_type: str = 'plain',
                       attachments: Optional[List[str]] = None, headers: Optional[Dict[str, str]] = None) -> Message:
        assert from_, 'from/from_ field not specified'

        body = MIMEText(body, body_type)
        if attachments:
            msg = MIMEMultipart()
            msg.attach(body)

            for attachment in attachments:
                attachment = os.path.abspath(os.path.expanduser(attachment))
                assert os.path.isfile(attachment), 'No such file: {}'.format(attachment)
                part = cls._file_to_part(attachment)
                part['Content-Disposition'] = 'attachment; filename="{}"'.format(os.path.basename(attachment))
                msg.attach(part)
        else:
            msg = body

        msg['From'] = from_
        msg['To'] = ', '.join(to) if isinstance(to, List) else to
        msg['Cc'] = ', '.join(cc) if cc else ''
        msg['Bcc'] = ', '.join(bcc) if bcc else ''
        msg['Subject'] = subject

        if headers:
            for name, value in headers.items():
                msg.add_header(name, value)

        return msg

    @action
    def send(self, to: Union[str, List[str]], from_: Optional[str] = None,
             cc: Optional[Union[str, List[str]]] = None, bcc: Optional[Union[str, List[str]]] = None,
             subject: str = '', body: str = '', body_type: str = 'plain', attachments: Optional[List[str]] = None,
             headers: Optional[Dict[str, str]] = None, **connect_args):
        """
        Send an email through the specified SMTP sender.

        :param to: Receiver(s), as comma-separated strings or list.
        :param from_: Sender email address (``from`` is also supported outside of Python contexts).
        :param cc: Carbon-copy addresses, as comma-separated strings or list
        :param bcc: Blind carbon-copy addresses, as comma-separated strings or list
        :param subject: Mail subject.
        :param body: Mail body.
        :param body_type: Mail body type, as a subtype of ``text/`` (e.g. ``html``) (default: ``plain``).
        :param attachments: List of attachment files to send.
        :param headers: Key-value map of headers to be added.
        :param connect_args: Parameters for ``.connect()``, if you want to override the default server configuration.
        """
        if not from_ and 'from' in connect_args:
            from_ = connect_args.pop('from')

        msg = self.create_message(to=to, from_=from_, cc=cc, bcc=bcc, subject=subject, body=body, body_type=body_type,
                                  attachments=attachments, headers=headers)

        return self.send_message(msg, **connect_args)


# vim:sw=4:ts=4:et:
