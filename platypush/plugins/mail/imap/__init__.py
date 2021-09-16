import email
from typing import Optional, List, Dict, Union, Any, Tuple

from imapclient import IMAPClient
from imapclient.response_types import Address

from platypush.plugins import action
from platypush.plugins.mail import MailInPlugin, ServerInfo, Mail


class MailImapPlugin(MailInPlugin):
    """
    Plugin to interact with a mail server over IMAP.

    Requires:

        * **imapclient** (``pip install imapclient``)

    """

    _default_port = 143
    _default_ssl_port = 993

    def __init__(self, server: str, port: Optional[int] = None, username: Optional[str] = None,
                 password: Optional[str] = None, password_cmd: Optional[str] = None, access_token: Optional[str] = None,
                 oauth_mechanism: Optional[str] = 'XOAUTH2', oauth_vendor: Optional[str] = None, ssl: bool = False,
                 keyfile: Optional[str] = None, certfile: Optional[str] = None, timeout: Optional[int] = 60, **kwargs):
        """
        :param server: Server name/address.
        :param port: Port (default: 143 for plain, 993 for SSL).
        :param username: IMAP username.
        :param password: IMAP password.
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
        self.server_info = self._get_server_info(server=server, port=port, username=username, password=password,
                                                 password_cmd=password_cmd, ssl=ssl, keyfile=keyfile, certfile=certfile,
                                                 access_token=access_token, oauth_mechanism=oauth_mechanism,
                                                 oauth_vendor=oauth_vendor, timeout=timeout)

    def _get_server_info(self, server: Optional[str] = None, port: Optional[int] = None, username: Optional[str] = None,
                         password: Optional[str] = None, password_cmd: Optional[str] = None,
                         access_token: Optional[str] = None, oauth_mechanism: Optional[str] = None,
                         oauth_vendor: Optional[str] = None, ssl: Optional[bool] = None, keyfile: Optional[str] = None,
                         certfile: Optional[str] = None, timeout: Optional[int] = None, **kwargs) -> ServerInfo:
        return super()._get_server_info(server=server, port=port, username=username, password=password,
                                        password_cmd=password_cmd, ssl=ssl, keyfile=keyfile, certfile=certfile,
                                        default_port=self._default_port, default_ssl_port=self._default_ssl_port,
                                        access_token=access_token, oauth_mechanism=oauth_mechanism,
                                        oauth_vendor=oauth_vendor, timeout=timeout)

    def connect(self, **connect_args) -> IMAPClient:
        info = self._get_server_info(**connect_args)
        self.logger.info('Connecting to {}'.format(info.server))
        context = None

        if info.ssl:
            import ssl
            context = ssl.create_default_context()
            context.load_cert_chain(certfile=info.certfile, keyfile=info.keyfile)

        client = IMAPClient(host=info.server, port=info.port, ssl=info.ssl, ssl_context=context)
        if info.password:
            client.login(info.username, info.password)
        elif info.access_token:
            client.oauth2_login(info.username, access_token=info.access_token, mech=info.oauth_mechanism,
                                vendor=info.oauth_vendor)

        return client

    @staticmethod
    def _get_folders(data: List[tuple]) -> List[Dict[str, str]]:
        folders = []
        for line in data:
            (flags), delimiter, mailbox_name = line
            folders.append({
                'name': mailbox_name,
                'flags': [flag.decode() for flag in flags],
                'delimiter': delimiter.decode(),
            })

        return folders

    @action
    def get_folders(self, folder: str = '', pattern: str = '*', **connect_args) -> List[Dict[str, str]]:
        """
        Get the list of all the folders hosted on the server or those matching a pattern.

        :param folder: Base folder (default: root).
        :param pattern: Pattern to search (default: None).
        :param connect_args: Arguments to pass to :meth:`._get_server_info` for server configuration override.
        :return: Example:

        .. code-block:: json

            [
                {
                    "name": "INBOX",
                    "flags": "\\Noinferiors",
                    "delimiter": "/"
                },
                {
                    "name": "Archive",
                    "flags": "\\Noinferiors",
                    "delimiter": "/"
                },
                {
                    "name": "Spam",
                    "flags": "\\Noinferiors",
                    "delimiter": "/"
                }
            ]

        """
        with self.connect(**connect_args) as client:
            data = client.list_folders(directory=folder, pattern=pattern)

        return self._get_folders(data)

    @action
    def get_sub_folders(self, folder: str = '', pattern: str = '*', **connect_args) -> List[Dict[str, str]]:
        """
        Get the list of all the sub-folders hosted on the server or those matching a pattern.

        :param folder: Base folder (default: root).
        :param pattern: Pattern to search (default: None).
        :param connect_args: Arguments to pass to :meth:`._get_server_info` for server configuration override.
        :return: Example:

        .. code-block:: json

            [
                {
                    "name": "INBOX",
                    "flags": "\\Noinferiors",
                    "delimiter": "/"
                },
                {
                    "name": "Archive",
                    "flags": "\\Noinferiors",
                    "delimiter": "/"
                },
                {
                    "name": "Spam",
                    "flags": "\\Noinferiors",
                    "delimiter": "/"
                }
            ]

        """
        with self.connect(**connect_args) as client:
            data = client.list_sub_folders(directory=folder, pattern=pattern)

        return self._get_folders(data)

    @staticmethod
    def _parse_address(imap_addr: Address) -> Dict[str, str]:
        return {
            'name': imap_addr.name.decode() if imap_addr.name else None,
            'route': imap_addr.route.decode() if imap_addr.route else None,
            'email': '{name}@{host}'.format(name=imap_addr.mailbox.decode(), host=imap_addr.host.decode())
        }

    @classmethod
    def _parse_addresses(cls, addresses: Optional[Tuple[Address]] = None) -> Dict[str, Dict[str, str]]:
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
            message['message_id'] = envelope.message_id.decode() if envelope.message_id else None
            message['in_reply_to'] = envelope.in_reply_to.decode() if envelope.in_reply_to else None
            message['reply_to'] = cls._parse_addresses(envelope.reply_to)
            message['sender'] = cls._parse_addresses(envelope.sender)
            message['subject'] = envelope.subject.decode() if envelope.subject else None
            message['to'] = cls._parse_addresses(envelope.to)

        return Mail(**message)

    @action
    def search(self, criteria: Union[str, List[str]] = 'ALL', folder: str = 'INBOX',
               attributes: Optional[List[str]] = None, **connect_args) -> List[Mail]:
        """
        Search for messages on the server that fit the specified criteria.

        :param criteria: It should be a sequence of one or more criteria items. Each criteria item may be either unicode
            or bytes (default: ``ALL``). Example values::

                ['UNSEEN']
                ['SMALLER', 500]
                ['NOT', 'DELETED']
                ['TEXT', 'foo bar', 'FLAGGED', 'SUBJECT', 'baz']
                ['SINCE', '2020-03-14T12:13:45+00:00']

            It is also possible (but not recommended) to pass the combined criteria as a single string. In this case
            IMAPClient won't perform quoting, allowing lower-level specification of criteria. Examples of this style::

                'UNSEEN'
                'SMALLER 500'
                'NOT DELETED'
                'TEXT "foo bar" FLAGGED SUBJECT "baz"'
                'SINCE 03-Apr-2005'

            To support complex search expressions, criteria lists can be nested. The following will match messages that
            are both not flagged and do not have "foo" in the subject::

                ['NOT', ['SUBJECT', 'foo', 'FLAGGED']]

        :param folder: Folder to search (default: ``INBOX``).
        :param attributes: Attributes that should be retrieved, according to
            `RFC 3501 <https://tools.ietf.org/html/rfc3501>`_
            (default: ``ALL`` = ``[FLAGS INTERNALDATE RFC822.SIZE ENVELOPE]``).
            Note that ``BODY`` will be ignored if specified here for performance reasons - use :meth:`.get_message` if
            you want to get the full content of a message known its ID from :meth:`.search`.

        :param connect_args: Arguments to pass to :meth:`._get_server_info` for server configuration override.
        :return: List of messages matching the criteria. Example:

        .. code-block:: json

            [
              {
                "id": 702,
                "seq": 671,
                "flags": [
                  "nonjunk"
                ],
                "internal_date": "2020-08-30T00:31:52+00:00",
                "size": 2908738,
                "bcc": {},
                "cc": {},
                "date": "2020-08-30T00:31:52+00:00",
                "from": {
                  "test123@gmail.com": {
                    "name": "A test",
                    "route": null,
                    "email": "test123@gmail.com"
                  }
                },
                "message_id": "<SOMETHING@mail.gmail.com>",
                "in_reply_to": "<SOMETHING@mail.gmail.com>",
                "reply_to": {},
                "sender": {
                  "test123@gmail.com": {
                    "name": "A test",
                    "route": null,
                    "email": "test123@gmail.com"
                  }
                },
                "subject": "Test email",
                "to": {
                  "me@gmail.com": {
                    "name": null,
                    "route": null,
                    "email": "me@gmail.com"
                  }
                }
              }
            ]

        """
        if not attributes:
            attributes = ['ALL']
        else:
            attributes = [attr.upper() for attr in attributes]

        data = {}
        with self.connect(**connect_args) as client:
            client.select_folder(folder, readonly=True)
            ids = client.search(criteria)
            if len(ids):
                data = client.fetch(list(ids), attributes)

        return [
            self._parse_message(msg_id, data[msg_id])
            for msg_id in sorted(data.keys())
        ]

    @action
    def search_unseen_messages(self, folder: str = 'INBOX', **connect_args) -> List[Mail]:
        """
        Shortcut for :meth:`.search` that returns only the unread messages.
        """
        return self.search(criteria='UNSEEN', directory=folder, attributes=['ALL'], **connect_args)

    @action
    def search_flagged_messages(self, folder: str = 'INBOX', **connect_args) -> List[Mail]:
        """
        Shortcut for :meth:`.search` that returns only the flagged/starred messages.
        """
        return self.search(criteria='Flagged', directory=folder, attributes=['ALL'], **connect_args)

    @action
    def search_starred_messages(self, folder: str = 'INBOX', **connect_args) -> List[Mail]:
        """
        Shortcut for :meth:`.search` that returns only the flagged/starred messages.
        """
        return self.search_flagged_messages(folder, **connect_args)

    @action
    def sort(self, folder: str = 'INBOX', sort_criteria: Union[str, List[str]] = 'ARRIVAL',
             criteria: Union[str, List[str]] = 'ALL', **connect_args) -> List[int]:
        """
        Return a list of message ids from the currently selected folder, sorted by ``sort_criteria`` and optionally
        filtered by ``criteria``. Note that SORT is an extension to the IMAP4 standard so it may not be supported by
        all IMAP servers.

        :param folder: Folder to be searched (default: ``INBOX``).
        :param sort_criteria: It may be a sequence of strings or a single string. IMAPClient will take care any required
            conversions. Valid *sort_criteria* values::

              .. code-block:: python

                ['ARRIVAL']
                ['SUBJECT', 'ARRIVAL']
                'ARRIVAL'
                'REVERSE SIZE'

        :param criteria: Optional filter for the messages, as specified in :meth:`.search`.
        :param connect_args: Arguments to pass to :meth:`._get_server_info` for server configuration override.
        :return: A list of message IDs that fit the criteria.
        """
        with self.connect(**connect_args) as client:
            client.select_folder(folder, readonly=True)
            msg_ids = client.sort(sort_criteria=sort_criteria, criteria=criteria)
            return msg_ids

    @action
    def get_message(self, message: int, folder: str = 'INBOX', **connect_args) -> Mail:
        """
        Get the full content of a message given the ID returned by :meth:`.search`.

        :param message: Message ID.
        :param folder: Folder name (default: ``INBOX``).
        :param connect_args: Arguments to pass to :meth:`._get_server_info` for server configuration override.
        :return: A message in the same format as :meth:`.search`, with an added ``payload`` attribute containing the
            body/payload.
        """
        with self.connect(**connect_args) as client:
            client.select_folder(folder, readonly=True)
            data = client.fetch(message, ['ALL', 'RFC822'])
            assert message in data, 'No such message ID: {}'.format(message)

            data = data[message]
            ret = self._parse_message(message, data)
            msg = email.message_from_bytes(data[b'RFC822'])
            ret.payload = msg.get_payload()

        return ret

    @action
    def create_folder(self, folder: str, **connect_args):
        """
        Create a folder on the server.

        :param folder: Folder name.
        :param connect_args:
        :param connect_args: Arguments to pass to :meth:`._get_server_info` for server configuration override.
        """
        with self.connect(**connect_args) as client:
            client.create_folder(folder)

    @action
    def rename_folder(self, old_name: str, new_name: str, **connect_args):
        """
        Rename a folder on the server.

        :param old_name: Previous name
        :param new_name: New name
        :param connect_args: Arguments to pass to :meth:`._get_server_info` for server configuration override.
        """
        with self.connect(**connect_args) as client:
            client.rename_folder(old_name, new_name)

    @action
    def delete_folder(self, folder: str, **connect_args):
        """
        Delete a folder from the server.

        :param folder: Folder name.
        :param connect_args: Arguments to pass to :meth:`._get_server_info` for server configuration override.
        """
        with self.connect(**connect_args) as client:
            client.delete_folder(folder)

    @staticmethod
    def _convert_flags(flags: Union[str, List[str]]) -> List[bytes]:
        if isinstance(flags, str):
            flags = [flag.strip() for flag in flags.split(',')]
        return [('\\' + flag).encode() for flag in flags]

    @action
    def add_flags(self, messages: List[int], flags: Union[str, List[str]], folder: str = 'INBOX', **connect_args):
        """
        Add a set of flags to the specified set of message IDs.

        :param messages: List of message IDs.
        :param flags: List of flags to be added. Examples:

          .. code-block:: python

            ['Flagged']
            ['Seen', 'Deleted']
            ['Junk']

        :param folder: IMAP folder (default: ``INBOX``).
        :param connect_args: Arguments to pass to :meth:`._get_server_info` for server configuration override.
        """
        with self.connect(**connect_args) as client:
            client.select_folder(folder)
            client.add_flags(messages, self._convert_flags(flags))

    @action
    def set_flags(self, messages: List[int], flags: Union[str, List[str]], folder: str = 'INBOX', **connect_args):
        """
        Set a set of flags to the specified set of message IDs.

        :param messages: List of message IDs.
        :param flags: List of flags to be added. Examples:

          .. code-block:: python

            ['Flagged']
            ['Seen', 'Deleted']
            ['Junk']

        :param folder: IMAP folder (default: ``INBOX``).
        :param connect_args: Arguments to pass to :meth:`._get_server_info` for server configuration override.
        """
        with self.connect(**connect_args) as client:
            client.select_folder(folder)
            client.set_flags(messages, self._convert_flags(flags))

    @action
    def remove_flags(self, messages: List[int], flags: Union[str, List[str]], folder: str = 'INBOX', **connect_args):
        """
        Remove a set of flags to the specified set of message IDs.

        :param messages: List of message IDs.
        :param flags: List of flags to be added. Examples:

          .. code-block:: python

            ['Flagged']
            ['Seen', 'Deleted']
            ['Junk']

        :param folder: IMAP folder (default: ``INBOX``).
        :param connect_args: Arguments to pass to :meth:`._get_server_info` for server configuration override.
        """
        with self.connect(**connect_args) as client:
            client.select_folder(folder)
            client.remove_flags(messages, self._convert_flags(flags))

    @action
    def flag_messages(self, messages: List[int], folder: str = 'INBOX', **connect_args):
        """
        Add a flag/star to the specified set of message IDs.

        :param messages: List of message IDs.
        :param folder: IMAP folder (default: ``INBOX``).
        :param connect_args: Arguments to pass to :meth:`._get_server_info` for server configuration override.
        """
        return self.add_flags(messages, ['Flagged'], folder=folder, **connect_args)

    @action
    def unflag_messages(self, messages: List[int], folder: str = 'INBOX', **connect_args):
        """
        Remove a flag/star from the specified set of message IDs.

        :param messages: List of message IDs.
        :param folder: IMAP folder (default: ``INBOX``).
        :param connect_args: Arguments to pass to :meth:`._get_server_info` for server configuration override.
        """
        return self.remove_flags(messages, ['Flagged'], folder=folder, **connect_args)

    @action
    def flag_message(self, message: int, folder: str = 'INBOX', **connect_args):
        """
        Add a flag/star to the specified set of message ID.

        :param message: Message ID.
        :param folder: IMAP folder (default: ``INBOX``).
        :param connect_args: Arguments to pass to :meth:`._get_server_info` for server configuration override.
        """
        return self.flag_messages([message], folder=folder, **connect_args)

    @action
    def unflag_message(self, message: int, folder: str = 'INBOX', **connect_args):
        """
        Remove a flag/star from the specified set of message ID.

        :param message: Message ID.
        :param folder: IMAP folder (default: ``INBOX``).
        :param connect_args: Arguments to pass to :meth:`._get_server_info` for server configuration override.
        """
        return self.unflag_messages([message], folder=folder, **connect_args)

    @action
    def delete_messages(self, messages: List[int], folder: str = 'INBOX', expunge: bool = True, **connect_args):
        """
        Set a specified set of message IDs as deleted.

        :param messages: List of message IDs.
        :param folder: IMAP folder (default: ``INBOX``).
        :param expunge: If set then the messages will also be expunged from the folder, otherwise they will only be
            marked as deleted (default: ``True``).
        :param connect_args: Arguments to pass to :meth:`._get_server_info` for server configuration override.
        """
        self.add_flags(messages, ['Deleted'], folder=folder, **connect_args)
        if expunge:
            self.expunge_messages(folder=folder, messages=messages, **connect_args)

    @action
    def undelete_messages(self, messages: List[int], folder: str = 'INBOX', **connect_args):
        """
        Remove the ``Deleted`` flag from the specified set of message IDs.

        :param messages: List of message IDs.
        :param folder: IMAP folder (default: ``INBOX``).
        :param connect_args: Arguments to pass to :meth:`._get_server_info` for server configuration override.
        """
        return self.remove_flags(messages, ['Deleted'], folder=folder, **connect_args)

    @action
    def copy_messages(self, messages: List[int], dest_folder: str, source_folder: str = 'INBOX', **connect_args):
        """
        Copy a set of messages IDs from a folder to another.

        :param messages: List of message IDs.
        :param source_folder: Source folder.
        :param dest_folder: Destination folder.
        :param connect_args: Arguments to pass to :meth:`._get_server_info` for server configuration override.
        """
        with self.connect(**connect_args) as client:
            client.select_folder(source_folder)
            client.copy(messages, dest_folder)

    @action
    def move_messages(self, messages: List[int], dest_folder: str, source_folder: str = 'INBOX', **connect_args):
        """
        Move a set of messages IDs from a folder to another.

        :param messages: List of message IDs.
        :param source_folder: Source folder.
        :param dest_folder: Destination folder.
        :param connect_args: Arguments to pass to :meth:`._get_server_info` for server configuration override.
        """
        with self.connect(**connect_args) as client:
            client.select_folder(source_folder)
            client.move(messages, dest_folder)

    @action
    def expunge_messages(self, folder: str = 'INBOX', messages: Optional[List[int]] = None, **connect_args):
        """
        When ``messages`` is not set, remove all the messages from ``folder`` marked as ``Deleted``.

        :param folder: IMAP folder (default: ``INBOX``).
        :param messages: List of message IDs to expunge (default: all those marked as ``Deleted``).
        :param connect_args: Arguments to pass to :meth:`._get_server_info` for server configuration override.
        """
        with self.connect(**connect_args) as client:
            client.select_folder(folder)
            client.expunge(messages)


# vim:sw=4:ts=4:et:
