import os

from abc import ABC, abstractmethod
from datetime import datetime
from email.message import Message
from email.mime.application import MIMEApplication
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from mimetypes import guess_type
from typing import Dict, Optional, Sequence, Union

from dateutil import tz

from .._utils import normalize_from_header
from ._base import BaseMailPlugin


class MailOutPlugin(BaseMailPlugin, ABC):
    """
    Base class for mail out plugins.
    """

    @abstractmethod
    def send_message(self, message: Message, **_):
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
    def create_message(
        cls,
        to: Union[str, Sequence[str]],
        from_: Optional[str] = None,
        cc: Optional[Union[str, Sequence[str]]] = None,
        bcc: Optional[Union[str, Sequence[str]]] = None,
        subject: str = '',
        body: str = '',
        body_type: str = 'plain',
        attachments: Optional[Sequence[str]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Message:
        assert from_, 'from/from_ field not specified'

        content = MIMEText(body, body_type)
        if attachments:
            msg = MIMEMultipart()
            msg.attach(content)

            for attachment in attachments:
                attachment = os.path.abspath(os.path.expanduser(attachment))
                assert os.path.isfile(attachment), f'No such file: {attachment}'
                part = cls._file_to_part(attachment)
                part[
                    'Content-Disposition'
                ] = f'attachment; filename="{os.path.basename(attachment)}"'
                msg.attach(part)
        else:
            msg = content

        msg['From'] = from_
        msg['To'] = to if isinstance(to, str) else ', '.join(to)
        msg['Cc'] = ', '.join(cc) if cc else ''
        msg['Bcc'] = ', '.join(bcc) if bcc else ''
        msg['Subject'] = subject
        msg['Date'] = (
            datetime.now()
            .replace(tzinfo=tz.tzlocal())
            .strftime('%a, %d %b %Y %H:%M:%S %z')
        )

        if headers:
            for name, value in headers.items():
                msg.add_header(name, value)

        return msg

    def send(
        self,
        to: Union[str, Sequence[str]],
        from_: Optional[str] = None,
        cc: Optional[Union[str, Sequence[str]]] = None,
        bcc: Optional[Union[str, Sequence[str]]] = None,
        subject: str = '',
        body: str = '',
        body_type: str = 'plain',
        attachments: Optional[Sequence[str]] = None,
        headers: Optional[Dict[str, str]] = None,
        **args,
    ):
        if not from_ and 'from' in args:
            from_ = args.pop('from')

        msg = self.create_message(
            to=to,
            from_=normalize_from_header(from_, self.account, self.server),
            cc=cc,
            bcc=bcc,
            subject=subject,
            body=body,
            body_type=body_type,
            attachments=attachments,
            headers=headers,
        )

        return self.send_message(msg, **args)


# vim:sw=4:ts=4:et:
