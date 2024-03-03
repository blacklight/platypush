import ssl

from contextlib import contextmanager
from typing import Generator, Iterable, Optional, List, Dict, Union, Any, Tuple

from imapclient import IMAPClient
from imapclient.response_types import Address

from .._model import Mail, TransportEncryption
from .._plugin import MailInPlugin


class MailImapPlugin(MailInPlugin):
    """
    Plugin to interact with a mail server over IMAP.
    """

    @classmethod
    def _matches_url_scheme(cls, scheme: str) -> bool:
        return scheme in ('imap', 'imaps')

    @classmethod
    def default_ports(cls) -> Dict[TransportEncryption, int]:
        return {
            TransportEncryption.NONE: 143,
            TransportEncryption.SSL: 993,
        }

    @contextmanager
    def connect(self) -> Generator[IMAPClient, None, None]:
        has_ssl = self.server.encryption == TransportEncryption.SSL
        context = None
        if has_ssl and self.server.certfile:
            context = ssl.create_default_context()
            context.load_cert_chain(
                certfile=self.server.certfile, keyfile=self.server.keyfile
            )

        client = IMAPClient(
            host=self.server.server,
            port=self.server.port,
            ssl=has_ssl,
            ssl_context=context,
        )

        if self.account.access_token:
            client.oauth2_login(
                self.account.username,
                access_token=self.account.access_token,
                mech=self.account.oauth_mechanism or 'XOAUTH2',
                vendor=self.account.oauth_vendor,
            )
        else:
            pwd = self.account.get_password()
            client.login(self.account.username, pwd)

        yield client
        client.logout()

    @staticmethod
    def _get_folders(data: List[tuple]) -> List[Dict[str, str]]:
        folders = []
        for line in data:
            (flags), delimiter, mailbox_name = line
            folders.append(
                {
                    'name': mailbox_name,
                    'flags': [flag.decode() for flag in flags],
                    'delimiter': delimiter.decode(),
                }
            )

        return folders

    @staticmethod
    def _parse_address(imap_addr: Address) -> Dict[str, Optional[str]]:
        return {
            'name': imap_addr.name.decode() if imap_addr.name else None,
            'route': imap_addr.route.decode() if imap_addr.route else None,
            'email': imap_addr.mailbox.decode() + '@' + imap_addr.host.decode(),
        }

    @classmethod
    def _parse_addresses(
        cls, addresses: Optional[Tuple[Address]] = None
    ) -> Dict[str, Dict[str, str]]:
        ret = {}
        if addresses:
            for addr in addresses:
                addr = cls._parse_address(addr)
                ret[addr['email']] = addr

        return ret

    @classmethod
    def _parse_message(cls, msg_id: int, imap_msg: Dict[bytes, Any]) -> Mail:
        message = {
            'id': msg_id,
            'seq': imap_msg[b'SEQ'],
        }

        if imap_msg.get(b'FLAGS'):
            message['flags'] = [flag.decode() for flag in imap_msg[b'FLAGS'] if flag]
        if b'INTERNALDATE' in imap_msg:
            message['internal_date'] = imap_msg[b'INTERNALDATE']
        if b'RFC822.SIZE' in imap_msg:
            message['size'] = imap_msg[b'RFC822.SIZE']
        if b'ENVELOPE' in imap_msg:
            envelope = imap_msg[b'ENVELOPE']
            message['bcc'] = cls._parse_addresses(envelope.bcc)
            message['cc'] = cls._parse_addresses(envelope.cc)
            message['date'] = envelope.date
            message['from'] = cls._parse_addresses(envelope.from_)
            message['message_id'] = (
                envelope.message_id.decode() if envelope.message_id else None
            )
            message['in_reply_to'] = (
                envelope.in_reply_to.decode() if envelope.in_reply_to else None
            )
            message['reply_to'] = cls._parse_addresses(envelope.reply_to)
            message['sender'] = cls._parse_addresses(envelope.sender)
            message['subject'] = envelope.subject.decode() if envelope.subject else None
            message['to'] = cls._parse_addresses(envelope.to)
        if b'BODY[]' in imap_msg:
            message['content'] = imap_msg[b'BODY[]']

        return Mail(**message)

    @staticmethod
    def _convert_flags(flags: Union[str, Iterable[str]]) -> List[bytes]:
        if isinstance(flags, str):
            flags = [flag.strip() for flag in flags.split(',')]
        return [('\\' + flag).encode() for flag in flags]

    def get_folders(
        self, folder: str = '', pattern: str = '*', **_
    ) -> List[Dict[str, str]]:
        with self.connect() as client:
            data = client.list_folders(directory=folder, pattern=pattern)

        return self._get_folders(data)

    def get_sub_folders(
        self, folder: str = '', pattern: str = '*', **_
    ) -> List[Dict[str, str]]:
        with self.connect() as client:
            data = client.list_sub_folders(directory=folder, pattern=pattern)

        return self._get_folders(data)

    def search(
        self,
        criteria: Union[str, Iterable[str]] = 'ALL',
        folder: str = 'INBOX',
        attributes: Optional[Iterable[str]] = None,
        **_,
    ) -> List[Mail]:
        if not attributes:
            attributes = ['FLAGS', 'INTERNALDATE', 'RFC822.SIZE', 'ENVELOPE']
        else:
            attributes = [attr.upper() for attr in attributes]

        data = {}
        with self.connect() as client:
            client.select_folder(folder, readonly=True)
            ids = client.search(criteria)  # type: ignore
            if ids:
                data = client.fetch(list(ids), attributes)

        return [
            self._parse_message(msg_id, data[msg_id]) for msg_id in sorted(data.keys())
        ]

    def search_unseen_messages(self, folder: str = 'INBOX') -> List[Mail]:
        return self.search(criteria='UNSEEN', directory=folder)

    def search_flagged_messages(self, folder: str = 'INBOX', **_) -> List[Mail]:
        return self.search(criteria='Flagged', directory=folder)

    def search_starred_messages(self, folder: str = 'INBOX', **_) -> List[Mail]:
        return self.search_flagged_messages(folder)

    def sort(
        self,
        folder: str = 'INBOX',
        sort_criteria: Union[str, Iterable[str]] = 'ARRIVAL',
        criteria: Union[str, Iterable[str]] = 'ALL',
    ) -> List[int]:
        with self.connect() as client:
            client.select_folder(folder, readonly=True)
            msg_ids = client.sort(sort_criteria=sort_criteria, criteria=criteria)  # type: ignore
            return msg_ids

    def get_messages(
        self,
        *ids: int,
        folder: str = 'INBOX',
        with_body: bool = True,
        **_,
    ) -> Dict[int, Mail]:
        ret = {}
        with self.connect() as client:
            client.select_folder(folder, readonly=True)
            attrs = ['FLAGS', 'RFC822.SIZE', 'INTERNALDATE', 'ENVELOPE']
            if with_body:
                attrs.append('BODY[]')

            data = client.fetch(ids, attrs)
            for id in ids:  # pylint: disable=redefined-builtin
                msg = data.get(id)
                if not msg:
                    continue

                ret[id] = self._parse_message(id, msg)

        return ret

    def create_folder(self, folder: str, **_):
        with self.connect() as client:
            client.create_folder(folder)

    def rename_folder(self, old_name: str, new_name: str, **_):
        with self.connect() as client:
            client.rename_folder(old_name, new_name)

    def delete_folder(self, folder: str, **_):
        with self.connect() as client:
            client.delete_folder(folder)

    def add_flags(
        self,
        messages: List[int],
        flags: Union[str, Iterable[str]],
        folder: str = 'INBOX',
        **_,
    ):
        with self.connect() as client:
            client.select_folder(folder)
            client.add_flags(messages, self._convert_flags(flags))

    def set_flags(
        self,
        messages: List[int],
        flags: Union[str, Iterable[str]],
        folder: str = 'INBOX',
        **_,
    ):
        with self.connect() as client:
            client.select_folder(folder)
            client.set_flags(messages, self._convert_flags(flags))

    def remove_flags(
        self,
        messages: List[int],
        flags: Union[str, Iterable[str]],
        folder: str = 'INBOX',
        **_,
    ):
        with self.connect() as client:
            client.select_folder(folder)
            client.remove_flags(messages, self._convert_flags(flags))

    def flag_messages(self, messages: List[int], folder: str = 'INBOX', **_):
        return self.add_flags(messages, ['Flagged'], folder=folder)

    def unflag_messages(self, messages: List[int], folder: str = 'INBOX', **_):
        return self.remove_flags(messages, ['Flagged'], folder=folder)

    def delete_messages(
        self,
        messages: List[int],
        folder: str = 'INBOX',
        expunge: bool = True,
        **_,
    ):
        self.add_flags(messages, ['Deleted'], folder=folder)
        if expunge:
            self.expunge_messages(folder=folder, messages=messages)

    def restore_messages(self, messages: List[int], folder: str = 'INBOX', **_):
        return self.remove_flags(messages, ['Deleted'], folder=folder)

    def copy_messages(
        self,
        messages: List[int],
        dest_folder: str,
        source_folder: str = 'INBOX',
        **_,
    ):
        with self.connect() as client:
            client.select_folder(source_folder)
            client.copy(messages, dest_folder)

    def move_messages(
        self,
        messages: List[int],
        dest_folder: str,
        source_folder: str = 'INBOX',
        **_,
    ):
        with self.connect() as client:
            client.select_folder(source_folder)
            client.move(messages, dest_folder)

    def expunge_messages(
        self,
        folder: str = 'INBOX',
        messages: Optional[List[int]] = None,
        **_,
    ):
        with self.connect() as client:
            client.select_folder(folder)
            client.expunge(messages)


# vim:sw=4:ts=4:et:
