import base64
import email
import logging
import json
from email.message import Message

from collections import defaultdict
from datetime import datetime
from enum import Enum
from typing import Any, Dict, IO, List, Optional, Union

from platypush.message import JSONAble

logger = logging.getLogger(__name__)

_text_types = {
    'text/plain',
    'text/html',
    'text/rtf',
    'text/enriched',
    'text/markdown',
    'application/rtf',
}


class Mail(JSONAble):  # pylint: disable=too-few-public-methods
    """
    Model for a mail message.
    """

    def __init__(
        self,
        id: int,  # pylint: disable=redefined-builtin
        date: datetime,
        size: int,
        from_: Optional[Union[Dict[str, str], List[str]]] = None,
        to: Optional[Union[Dict[str, str], List[str]]] = None,
        cc: Optional[Union[Dict[str, str], List[str]]] = None,
        bcc: Optional[Union[Dict[str, str], List[str]]] = None,
        subject: str = '',
        content: Optional[Any] = None,
        **kwargs,
    ):
        self.id = id
        self.date = date
        self.size = size
        self.from_ = from_ or kwargs.pop('from', None)
        self.to = to
        self.cc = cc or []
        self.bcc = bcc or []
        self.subject = subject
        self._content = content
        self.args = kwargs

    @staticmethod
    def _parse_body(msg: Message) -> str:
        body = ''
        if msg.is_multipart():
            for part in msg.walk():
                if (
                    part.get_content_type() in _text_types
                    and
                    # skip any text/plain (txt) attachments
                    'attachment' not in part.get('Content-Disposition', '')
                ):
                    body = bytes(part.get_payload(decode=True)).decode()
                    break
        else:
            body = bytes(msg.get_payload(decode=True)).decode()

        return body

    @staticmethod
    def _parse_attachments(msg: Message) -> List[dict]:
        attachments = []
        if msg.is_multipart():
            for part in msg.walk():
                if 'attachment' not in part.get('Content-Disposition', ''):
                    continue

                raw_payload = bytes(part.get_payload(decode=True))
                try:
                    # Try to decode it as a string
                    payload = raw_payload.decode()
                except UnicodeDecodeError:
                    # Otherwise, return a JSON-encoded string
                    payload = base64.b64encode(raw_payload).decode()

                attachments.append(
                    {
                        'filename': part.get_filename(),
                        'headers': dict(part),
                        'body': payload,
                    }
                )

        return attachments

    @classmethod
    def _parse_payload(cls, payload: Union[bytes, bytearray]) -> dict:
        msg = email.message_from_bytes(payload)
        return {
            'headers': dict(msg),
            'body': cls._parse_body(msg),
            'attachments': cls._parse_attachments(msg),
        }

    @property
    def content(self):
        if isinstance(self._content, (bytes, bytearray)):
            try:
                return self._parse_payload(self._content)
            except Exception as e:
                logger.warning(
                    'Error while parsing payload for message ID %s: %s', self.id, e
                )
                logger.exception(e)

        return self._content

    def to_json(self) -> dict:
        return {
            'id': self.id,
            'date': self.date,
            'size': self.size,
            'from': self.from_,
            'to': self.to,
            'cc': self.cc,
            'bcc': self.bcc,
            'subject': self.subject,
            'content': self.content,
            **self.args,
        }


class MailFlagType(Enum):
    """
    Types of supported mail flags.
    """

    FLAGGED = 'flagged'
    UNREAD = 'unread'


FolderStatus = Dict[MailFlagType, Dict[int, Mail]]
FoldersStatus = Dict[str, FolderStatus]


class AccountsStatus:
    """
    Models the status of all the monitored mailboxes.
    """

    def __init__(self):
        self._dict: Dict[str, FoldersStatus] = defaultdict(
            lambda: defaultdict(lambda: {evt: {} for evt in MailFlagType})
        )

    class Serializer(json.JSONEncoder):
        def default(self, o):
            if isinstance(o, datetime):
                return o.isoformat()
            if isinstance(o, MailFlagType):
                return o.value
            return json.JSONEncoder.default(self, o)

    class Deserializer(json.JSONDecoder):
        def __init__(self):
            super().__init__(object_hook=self._hook)

        @staticmethod
        def _hook(o):
            if 'date' in o:
                o['date'] = datetime.fromisoformat(o['date'])
            if 'flag' in o:
                o['flag'] = MailFlagType(o['flag'])
            return o

    def __getitem__(self, item: str) -> FoldersStatus:
        return self._dict[item]

    def __setitem__(self, key: str, value: FoldersStatus):
        self._dict[key] = value

    def __delitem__(self, key: str) -> None:
        del self._dict[key]

    def __iter__(self):
        return iter(self._dict)

    def __len__(self) -> int:
        return len(self._dict)

    def __contains__(self, item) -> bool:
        return item in self._dict

    def __str__(self):
        return json.dumps(self._dict, cls=self.Serializer)

    def __repr__(self):
        return self.__str__()

    def items(self):
        return self._dict.items()

    def copy(self) -> 'AccountsStatus':
        obj = AccountsStatus()
        obj._dict.update(
            {
                account: {
                    folder: {MailFlagType(evt): msgs for evt, msgs in statuses.items()}
                    for folder, statuses in folders.items()
                }
                for account, folders in self._dict.items()
            }
        )
        return obj

    def get(self, key: str, default=None) -> Optional[FoldersStatus]:
        return self._dict.get(key, default)

    @classmethod
    def read(cls, f: IO) -> 'AccountsStatus':
        obj = cls()
        obj._dict.update(
            {
                account: {
                    folder: {MailFlagType(evt): msgs for evt, msgs in statuses.items()}
                    for folder, statuses in folders.items()
                }
                for account, folders in json.load(f, cls=cls.Deserializer).items()
            }
        )
        return obj

    def write(self, f: IO):
        f.write(
            json.dumps(
                {
                    account: {
                        folder: {
                            evt.value: {msg_id: {} for msg_id in msgs}
                            for evt, msgs in statuses.items()
                        }
                        for folder, statuses in folders.items()
                    }
                    for account, folders in self._dict.items()
                },
                cls=self.Serializer,
            )
        )


# vim:sw=4:ts=4:et:
