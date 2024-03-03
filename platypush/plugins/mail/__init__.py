import os
import pathlib
import time

from collections import defaultdict
from threading import Thread, RLock
from typing import Any, Dict, List, Optional, Union, Collection

from platypush.config import Config
from platypush.message.event.mail import (
    FlaggedMailEvent,
    SeenMailEvent,
    UnflaggedMailEvent,
    UnseenMailEvent,
)
from platypush.plugins import RunnablePlugin, action

from ._account import Account
from ._model import FolderStatus, Mail, MailFlagType, AccountsStatus
from ._plugin import MailInPlugin, MailOutPlugin

AccountType = Union[str, int, Account]
AccountFolderChanges = Dict[str, Dict[MailFlagType, Dict[int, bool]]]


class MailPlugin(RunnablePlugin):
    """
    Plugin to:

       - Monitor one or more mailboxes, and emit events when new messages are
         received, seen, flagged or unflagged.

       - Send mail messages.

       - Search for messages in a mailbox.

    """

    def __init__(
        self,
        accounts: List[Dict[str, Any]],
        timeout: float = 20.0,
        poll_interval: float = 60.0,
        **kwargs,
    ):
        """
        Example accounts configuration:

          .. code-block:: yaml

            mail:
                # Display name to be used for outgoing emails. Default:
                # the `from` parameter will be used from :meth:`.send`,
                # and, if missing, the username from the account configuration
                # will be used.
                display_name: My Name

                # How often we should poll for updates (default: 60 seconds)
                poll_interval: 60

                # Connection timeout (default: 20 seconds)
                # Can be overridden on a per-account basis
                timeout: 20

                # Domain to be used for outgoing emails. Default: inferred
                # from the account configuration
                domain: example.com

                accounts:
                    - name: "My Local Account"
                      username: me@mydomain.com
                      password: my-password

                      # The default flag sets this account as the default one
                      # for mail retrieval and sending if no account is
                      # specified on an action. If multiple accounts are set
                      # and none is set as default, and no account is specified
                      # on an action, then the first configured account will be
                      # used.
                      default: true

                      # Alternatively, you can run an external command
                      # to get the password
                      # password_cmd: "pass show mail/example.com"

                      # Path to a custom certfile if the mail server uses a
                      # self-signed certificate
                      # certfile: /path/to/certfile

                      # Path to a custom keyfile if the mail server requires
                      # client authentication. It requires certfile to be set
                      # too
                      # keyfile: /path/to/keyfile

                      incoming:
                          # Supported protocols: imap, imaps
                          server: imaps://mail.example.com:993

                      outgoing:
                          # The `incoming` and `outgoing` configurations can
                          # override the global `username` and `password` and
                          # other authentication parameters of the account
                          username: me
                          password: my-smtp-password

                          # Supported protocols: smtp, smtps, smtp+starttls,
                          server: smtps://mail.example.com:465

                      # These folders will be monitored for new messages
                      monitor_folders:
                          - All Mail

                    - name: "GMail"
                      username: me@gmail.com

                      # Access token, if the mail server supports OAuth2
                      # access_token: my-access-token

                      # OAuth mechanism, if the mail server supports OAuth2
                      # (default: XOAUTH2)
                      # oauth_mechanism: XOAUTH2

                      # OAuth vendor, if the mail server supports OAuth2
                      # oauth_vendor: GOOGLE

                      incoming:
                          # Defaults to port 993 for IMAPS if no port is
                          # specified on the URL
                          server: imaps://imap.gmail.com

                      outgoing:
                          # Defaults to port 465 for SMTPS if no port is
                          # specified on the URL
                          server: smtps://smtp.gmail.com

                      monitor_folders:
                          - INBOX
                          - Sent

        :param accounts: List of available mailboxes/accounts.
        :param poll_interval: How often the plugin should poll for new messages
            (default: 60 seconds).
        :param timeout: Timeout for the mail server connection (default: 20
            seconds).
        """
        assert accounts, 'No mail accounts configured'

        super().__init__(poll_interval=poll_interval, **kwargs)
        self.timeout = timeout
        self.accounts = self._parse_accounts(accounts)
        self._accounts_by_name = {acc.name: acc for acc in self.accounts}
        self._default_account = next(
            (acc for acc in self.accounts if acc.default), self.accounts[0]
        )

        self._status = AccountsStatus()
        self._db_lock = RLock()
        self.workdir = os.path.join(Config.get_workdir(), 'mail')
        self._status_file = os.path.join(self.workdir, 'status.json')

        # Configure/sync db
        pathlib.Path(self.workdir).mkdir(parents=True, exist_ok=True, mode=0o750)
        self._load_status()

    def _load_status(self):
        with self._db_lock:
            try:
                with open(self._status_file) as f:
                    self._status = AccountsStatus.read(f)
            except FileNotFoundError:
                self._status = AccountsStatus()
            except Exception as e:
                self.logger.warning(
                    'Could not load mail status from %s: %s', self._status_file, e
                )
                self._status = AccountsStatus()

    def _get_account(self, account: Optional[AccountType] = None) -> Account:
        if isinstance(account, Account):
            return account

        if isinstance(account, int):
            account -= 1
            assert (
                0 <= account < len(self.accounts)
            ), f'Invalid account index {account} (valid range: 1-{len(self.accounts)})'

            return self.accounts[account]

        if isinstance(account, str):
            acc = self._accounts_by_name.get(account)
            assert acc, f'No account found with name "{account}"'
            return acc

        return self._default_account

    def _get_in_plugin(self, account: Optional[AccountType] = None) -> MailInPlugin:
        acc = self._get_account(account)
        assert acc.incoming, f'No incoming configuration found for account "{acc.name}"'
        return acc.incoming

    def _get_out_plugin(self, account: Optional[AccountType] = None) -> MailOutPlugin:
        acc = self._get_account(account)
        assert acc.outgoing, f'No outgoing configuration found for account "{acc.name}"'
        return acc.outgoing

    def _parse_accounts(self, accounts: List[Dict[str, Any]]) -> List[Account]:
        ret = []
        for i, acc in enumerate(accounts):
            idx = i + 1
            name = acc.pop('name') if 'name' in acc else f'Account #{idx}'
            incoming_conf = acc.pop('incoming')
            outgoing_conf = acc.pop('outgoing')
            monitor_folders = acc.pop('monitor_folders', [])

            assert (
                incoming_conf or outgoing_conf
            ), f'No incoming/outgoing configuration specified for account "{name}"'

            if monitor_folders:
                assert incoming_conf, (
                    f'Cannot monitor folders for account "{name}" '
                    'without incoming configuration'
                )

            acc['poll_interval'] = self.poll_interval
            acc['timeout'] = acc.get('timeout', self.timeout)
            ret.append(
                Account.build(
                    name=name,
                    incoming=incoming_conf,
                    outgoing=outgoing_conf,
                    monitor_folders=monitor_folders,
                    **acc,
                )
            )

        return ret

    @property
    def _monitored_accounts(self):
        return [acc for acc in self.accounts if acc.monitor_folders]

    @property
    def _account_by_name(self) -> Dict[str, Account]:
        return {acc.name: acc for acc in self.accounts}

    @staticmethod
    def _check_thread(plugin: MailInPlugin, folder: str, results: FolderStatus):
        results[MailFlagType.UNREAD] = {
            msg.id: msg for msg in plugin.search_unseen_messages(folder=folder)
        }

        results[MailFlagType.FLAGGED] = {
            msg.id: msg for msg in plugin.search_flagged_messages(folder=folder)
        }

    def _check_mailboxes(self) -> AccountsStatus:
        # Workers indexed by (account_name, folder) -> thread
        workers = {}
        status = AccountsStatus()

        for account in self._monitored_accounts:
            for folder in account.monitor_folders or []:
                worker = Thread(
                    target=self._check_thread,
                    name=f'check-mailbox-{account.name}-{folder}',
                    kwargs={
                        'plugin': account.incoming,
                        'results': status[account.name][folder],
                        'folder': folder,
                    },
                )

                worker.start()
                workers[account.name, folder] = worker

        wait_start = time.time()
        for worker_key, worker in workers.items():
            account = self._account_by_name[worker_key[0]]
            if not account.incoming:
                continue

            # The timeout should be the time elapsed since wait_start + the configured timeout
            timeout = max(
                0, account.incoming.server.timeout - (time.time() - wait_start)
            )
            worker.join(timeout=timeout)
            if worker.is_alive():
                self.logger.warning('Timeout while polling account %s', account.name)

        return status

    @action
    def get_folders(
        self,
        folder: str = '',
        pattern: str = '*',
        account: Optional[AccountType] = None,
    ) -> List[Dict[str, str]]:
        r"""
        Get the list of all the folders hosted on the server or those matching a pattern.

        :param folder: Base folder (default: root).
        :param pattern: Pattern to search (default: None).
        :param account: Account name or index (default: default account).
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
        return self._get_in_plugin(account).get_folders(folder=folder, pattern=pattern)

    @action
    def get_sub_folders(
        self,
        folder: str = '',
        pattern: str = '*',
        account: Optional[AccountType] = None,
    ) -> List[Dict[str, str]]:
        r"""
        Get the list of all the sub-folders hosted on the server or those matching a pattern.

        :param folder: Base folder (default: root).
        :param pattern: Pattern to search (default: None).
        :param account: Account name or index (default: default account).
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
        return self._get_in_plugin(account).get_sub_folders(
            folder=folder, pattern=pattern
        )

    @action
    def search(
        self,
        criteria: Union[str, List[str]] = 'ALL',
        folder: str = 'INBOX',
        attributes: Optional[List[str]] = None,
        account: Optional[AccountType] = None,
    ) -> List[Mail]:
        """
        Search for messages on the server that fit the specified criteria.

        If no criteria is specified, then all the messages in the folder will
        be returned.

        :param criteria: It should be a sequence of one or more criteria items.
            Each criterion item may be either unicode or bytes (default:
            ``ALL``). Example values::

                ['UNSEEN']
                ['FROM', 'me@example.com']
                ['TO', 'me@example.com']
                ['SMALLER', 500]
                ['NOT', 'DELETED']
                ['TEXT', 'foo bar', 'FLAGGED', 'SUBJECT', 'baz']
                ['SINCE', '2020-03-14T12:13:45+00:00']

            It is also possible (but not recommended) to pass the combined
            criteria as a single string. In this case IMAPClient won't perform
            quoting, allowing lower-level specification of criteria. Examples
            of this style::

                'UNSEEN'
                'SMALLER 500'
                'NOT DELETED'
                'TEXT "foo bar" FLAGGED SUBJECT "baz"'
                'SINCE 03-Apr-2005'

            To support complex search expressions, criteria lists can be
            nested. The following will match messages that are both not flagged
            and do not have "foo" in the subject::

                ['NOT', ['SUBJECT', 'foo', 'FLAGGED']]

            See :rfc:`3501#section-6.4.4` for more details.

        :param folder: Folder to search (default: ``INBOX``).
        :param attributes: Attributes that should be retrieved, according to
            `RFC 3501 <https://tools.ietf.org/html/rfc3501>`_
            (default: ``ALL`` = ``[FLAGS INTERNALDATE RFC822.SIZE ENVELOPE]``).
            Note that ``BODY`` will be ignored if specified here for
            performance reasons - use :meth:`.get_message` if you want to get
            the full content of a message known its ID from :meth:`.search`.

        :param account: Account name or index (default: default account).
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
        return self._get_in_plugin(account).search(
            criteria=criteria, folder=folder, attributes=attributes
        )

    @action
    def search_unseen_messages(
        self, folder: str = 'INBOX', account: Optional[AccountType] = None
    ) -> List[Mail]:
        """
        Shortcut for :meth:`.search` that returns only the unread messages.
        """
        return self._get_in_plugin(account).search_unseen_messages(folder=folder)

    @action
    def search_flagged_messages(
        self, folder: str = 'INBOX', account: Optional[AccountType] = None
    ) -> List[Mail]:
        """
        Shortcut for :meth:`.search` that returns only the flagged/starred messages.
        """
        return self._get_in_plugin(account).search_flagged_messages(folder=folder)

    @action
    def search_starred_messages(
        self, folder: str = 'INBOX', account: Optional[AccountType] = None
    ) -> List[Mail]:
        """
        Shortcut for :meth:`.search` that returns only the starred messages.
        """
        return self._get_in_plugin(account).search_starred_messages(folder=folder)

    @action
    def sort(
        self,
        folder: str = 'INBOX',
        sort_criteria: Union[str, List[str]] = 'ARRIVAL',
        criteria: Union[str, List[str]] = 'ALL',
        account: Optional[AccountType] = None,
    ) -> List[int]:
        """
        Return a list of message ids from the currently selected folder, sorted
        by ``sort_criteria`` and optionally filtered by ``criteria``. Note that
        SORT is an extension to the IMAP4 standard, so it may not be supported
        by all IMAP servers.

        :param folder: Folder to be searched (default: ``INBOX``).
        :param sort_criteria: It may be a sequence of strings or a single
            string. IMAPClient will take care any required conversions. Valid
            *sort_criteria* values::

              .. code-block:: python

                ['ARRIVAL']
                ['SUBJECT', 'ARRIVAL']
                'ARRIVAL'
                'REVERSE SIZE'

        :param criteria: Optional filter for the messages, as specified in
            :meth:`.search`.
        :param account: Account name or index (default: default account).
        :return: A list of message IDs that fit the criteria.
        """
        return self._get_in_plugin(account).sort(
            folder=folder, sort_criteria=sort_criteria, criteria=criteria
        )

    @action
    def get_message(
        self,
        id: int,  # pylint: disable=redefined-builtin
        folder: str = 'INBOX',
        account: Optional[AccountType] = None,
        with_body: bool = True,
    ) -> Mail:
        r"""
        Get the full content of a message given the ID returned by :meth:`.search`.

        :param id: Message ID.
        :param folder: Folder name (default: ``INBOX``).
        :param account: Account name or index (default: default account).
        :param with_body: If set then the body/payload will be included in the response (default: ``True``).
        :return: A message in the same format as :meth:`.search`, with an added
            ``payload`` attribute containing the body/payload. Example response:

            .. code-block:: json

                {
                  "id": 123,
                  "date": "2024-01-13T21:04:50",
                  "size": 3833,
                  "from": {
                    "you@example.com": {
                      "name": "Me",
                      "route": null,
                      "email": "you@example.com"
                    }
                  },
                  "to": {
                    "me@example.com": {
                      "name": "Me",
                      "route": null,
                      "email": "me@example.com"
                    }
                  },
                  "cc": {
                    "they@example.com": {
                      "name": "They",
                      "route": null,
                      "email": "they@example.com"
                    }
                  },
                  "bcc": {
                    "boss@example.com": {
                      "name": "Boss",
                      "route": null,
                      "email": "boss@example.com"
                    }
                  },
                  "subject": "Test email",
                  "content": {
                    "headers": {
                      "Return-Path": "<you@example.com>",
                      "Delivered-To": "me@example.com",
                      "Date": "Sat, 13 Jan 2024 20:04:50 +0000",
                      "To": "Me <me@example.com>",
                      "Cc": "They <they@example.com>",
                      "Bcc": "Boss <boss@example.com",
                      "From": "You <you@example.com>",
                      "Subject": "Test email",
                      "Message-ID": "<0123456789@client>",
                      "MIME-Version": "1.0",
                      "Content-Type": "multipart/mixed;\r\n boundary=\"0123456789\""
                    },
                    "body": "This is the email body",
                    "attachments": [
                      {
                        "filename": "signature.asc",
                        "headers": {
                          "Content-Type": "application/pgp-signature; name=signature.asc",
                          "Content-Transfer-Encoding": "base64",
                          "Content-Disposition": "attachment; filename=signature.asc"
                        },
                        "body": "-----BEGIN PGP SIGNATURE-----\r\n\r\n....\r\n\r\n-----END PGP SIGNATURE-----\r\n"
                      },
                      {
                        "filename": "image.jpg",
                        "body": "/9j/4gIcSUNDX1BST0ZJTEUAA...",
                        "headers": {
                          "Content-Type": "image/jpeg; Name=\"image.jpg\"",
                          "MIME-Version": "1.0",
                          "Content-Transfer-Encoding": "base64",
                          "Content-Disposition": "attachment; filename=\"profile_pic.jpg\""
                        }
                      }
                    ]
                  },
                  "seq": 123,
                  "internal_date": "2024-01-13T21:05:12",
                  "message_id": "<0123456789@client>",
                  "reply_to": {
                    "you@example.com": {
                      "name": "You",
                      "route": null,
                      "email": "you@example.com"
                    }
                  },
                  "sender": {
                    "you@example.com": {
                      "name": "You",
                      "route": null,
                      "email": "you@example.com"
                    }
                  }
                }

        """
        return self._get_in_plugin(account).get_message(
            id=id, folder=folder, with_body=with_body
        )

    @action
    def get_messages(
        self,
        ids: Collection[int],
        folder: str = 'INBOX',
        account: Optional[AccountType] = None,
        with_body: bool = True,
    ) -> Dict[int, Mail]:
        """
        Get the full content of a list of messages given their IDs returned by :meth:`.search`.

        :param ids: IDs of the messages to retrieve.
        :param folder: Folder name (default: ``INBOX``).
        :param account: Account name or index (default: default account).
        :param with_body: If set then the body/payload will be included in the response
            (default: ``True``).
        :return: A dictionary in the format ``{id -> msg}``, where ``msg`` is in the same
            format as :meth:`.search`, with an added ``payload`` attribute containing the
            body/payload. See :meth:`.get_message` for an example message format.
        """
        return self._get_in_plugin(account).get_messages(
            *ids, folder=folder, with_body=with_body
        )

    @action
    def create_folder(self, folder: str, account: Optional[AccountType] = None):
        """
        Create a folder on the server.

        :param folder: Folder name.
        :param account: Account name or index (default: default account).
        """
        return self._get_in_plugin(account).create_folder(folder=folder)

    @action
    def rename_folder(
        self, old_name: str, new_name: str, account: Optional[AccountType] = None
    ):
        """
        Rename a folder on the server.

        :param old_name: Previous name
        :param new_name: New name
        :param account: Account name or index (default: default account).
        """
        return self._get_in_plugin(account).rename_folder(
            old_name=old_name, new_name=new_name
        )

    @action
    def delete_folder(self, folder: str, account: Optional[AccountType] = None):
        """
        Delete a folder from the server.

        :param folder: Folder name.
        :param account: Account name or index (default: default account).
        """
        return self._get_in_plugin(account).delete_folder(folder=folder)

    @action
    def add_flags(
        self,
        messages: List[int],
        flags: Union[str, List[str]],
        folder: str = 'INBOX',
        account: Optional[AccountType] = None,
    ):
        """
        Add a set of flags to the specified set of message IDs.

        :param messages: List of message IDs.
        :param flags: List of flags to be added. Examples:

          .. code-block:: python

            ['Flagged']
            ['Seen', 'Deleted']
            ['Junk']

        :param folder: IMAP folder (default: ``INBOX``).
        :param account: Account name or index (default: default account).
        """
        return self._get_in_plugin(account).add_flags(
            messages=messages, flags=flags, folder=folder
        )

    @action
    def set_flags(
        self,
        messages: List[int],
        flags: Union[str, List[str]],
        folder: str = 'INBOX',
        account: Optional[AccountType] = None,
    ):
        """
        Set a set of flags to the specified set of message IDs.

        :param messages: List of message IDs.
        :param flags: List of flags to be added. Examples:

          .. code-block:: python

            ['Flagged']
            ['Seen', 'Deleted']
            ['Junk']

        :param folder: IMAP folder (default: ``INBOX``).
        :param account: Account name or index (default: default account).
        """
        return self._get_in_plugin(account).set_flags(
            messages=messages, flags=flags, folder=folder
        )

    @action
    def remove_flags(
        self,
        messages: List[int],
        flags: Union[str, List[str]],
        folder: str = 'INBOX',
        account: Optional[AccountType] = None,
    ):
        """
        Remove a set of flags to the specified set of message IDs.

        :param messages: List of message IDs.
        :param flags: List of flags to be added. Examples:

          .. code-block:: python

            ['Flagged']
            ['Seen', 'Deleted']
            ['Junk']

        :param folder: IMAP folder (default: ``INBOX``).
        :param account: Account name or index (default: default account).
        """
        return self._get_in_plugin(account).remove_flags(
            messages=messages, flags=flags, folder=folder
        )

    @action
    def flag_messages(
        self,
        messages: List[int],
        folder: str = 'INBOX',
        account: Optional[AccountType] = None,
    ):
        """
        Add a flag/star to the specified set of message IDs.

        :param messages: List of message IDs.
        :param folder: IMAP folder (default: ``INBOX``).
        :param account: Account name or index (default: default account).
        """
        return self._get_in_plugin(account).flag_messages(
            messages=messages, folder=folder
        )

    @action
    def unflag_messages(
        self,
        messages: List[int],
        folder: str = 'INBOX',
        account: Optional[AccountType] = None,
    ):
        """
        Remove a flag/star from the specified set of message IDs.

        :param messages: List of message IDs.
        :param folder: IMAP folder (default: ``INBOX``).
        :param account: Account name or index (default: default account).
        """
        return self._get_in_plugin(account).unflag_messages(
            messages=messages, folder=folder
        )

    @action
    def flag_message(
        self, message: int, folder: str = 'INBOX', account: Optional[AccountType] = None
    ):
        """
        Add a flag/star to the specified set of message ID.

        :param message: Message ID.
        :param folder: IMAP folder (default: ``INBOX``).
        :param account: Account name or index (default: default account).
        """
        return self._get_in_plugin(account).flag_message(message=message, folder=folder)

    @action
    def unflag_message(
        self, message: int, folder: str = 'INBOX', account: Optional[AccountType] = None
    ):
        """
        Remove a flag/star from the specified set of message ID.

        :param message: Message ID.
        :param folder: IMAP folder (default: ``INBOX``).
        :param account: Account name or index (default: default account).
        """
        return self._get_in_plugin(account).unflag_message(
            message=message, folder=folder
        )

    @action
    def delete_messages(
        self,
        messages: List[int],
        folder: str = 'INBOX',
        expunge: bool = True,
        account: Optional[AccountType] = None,
    ):
        """
        Set a specified set of message IDs as deleted.

        :param messages: List of message IDs.
        :param folder: IMAP folder (default: ``INBOX``).
        :param expunge: If set then the messages will also be expunged from the
            folder, otherwise they will only be marked as deleted (default:
            ``True``).
        :param account: Account name or index (default: default account).
        """
        return self._get_in_plugin(account).delete_messages(
            messages=messages, folder=folder, expunge=expunge
        )

    @action
    def restore_messages(
        self,
        messages: List[int],
        folder: str = 'INBOX',
        account: Optional[AccountType] = None,
    ):
        """
        Remove the ``Deleted`` flag from the specified set of message IDs.

        :param messages: List of message IDs.
        :param folder: IMAP folder (default: ``INBOX``).
        :param account: Account name or index (default: default account).
        """
        return self._get_in_plugin(account).restore_messages(
            messages=messages, folder=folder
        )

    @action
    def copy_messages(
        self,
        messages: List[int],
        destination: str,
        source: str = 'INBOX',
        account: Optional[AccountType] = None,
    ):
        """
        Copy a set of messages IDs from a folder to another.

        :param messages: List of message IDs.
        :param source: Source folder.
        :param destination: Destination folder.
        :param account: Account name or index (default: default account).
        """
        return self._get_in_plugin(account).copy_messages(
            messages=messages, dest_folder=destination, source_folder=source
        )

    @action
    def move_messages(
        self,
        messages: List[int],
        destination: str,
        source: str = 'INBOX',
        account: Optional[AccountType] = None,
    ):
        """
        Move a set of messages IDs from a folder to another.

        :param messages: List of message IDs.
        :param source: Source folder.
        :param destination: Destination folder.
        :param account: Account name or index (default: default account).
        """
        return self._get_in_plugin(account).move_messages(
            messages=messages, dest_folder=destination, source_folder=source
        )

    @action
    def expunge_messages(
        self,
        messages: List[int],
        folder: str = 'INBOX',
        account: Optional[AccountType] = None,
    ):
        """
        When ``messages`` is not set, remove all the messages from ``folder``
        marked as ``Deleted``.

        :param folder: IMAP folder (default: ``INBOX``).
        :param messages: List of message IDs to expunge (default: all those
            marked as ``Deleted``).
        :param account: Account name or index (default: default account).
        """
        return self._get_in_plugin(account).expunge_messages(
            folder=folder, messages=messages
        )

    @action
    def send(
        self,
        to: Union[str, List[str]],
        from_: Optional[str] = None,
        cc: Optional[Union[str, List[str]]] = None,
        bcc: Optional[Union[str, List[str]]] = None,
        subject: str = '',
        body: str = '',
        body_type: str = 'plain',
        attachments: Optional[List[str]] = None,
        headers: Optional[Dict[str, str]] = None,
        account: Optional[AccountType] = None,
        **kwargs,
    ):
        """
        Send an email through the specified SMTP sender.

        :param to: Receiver(s), as comma-separated strings or list.
        :param from_: Sender email address (``from`` is also supported).
        :param cc: Carbon-copy addresses, as comma-separated strings or list
        :param bcc: Blind carbon-copy addresses, as comma-separated strings or list
        :param subject: Mail subject.
        :param body: Mail body.
        :param body_type: Mail body type, as a subtype of ``text/`` (e.g. ``html``) (default: ``plain``).
        :param attachments: List of attachment files to send.
        :param headers: Key-value map of headers to be added.
        :param account: Account name/index to be used (default: default account).
        """
        plugin = self._get_out_plugin(account)
        headers = {k.lower(): v for k, v in (headers or {}).items()}
        cc = ([cc] if isinstance(cc, str) else cc) or []
        bcc = ([bcc] if isinstance(bcc, str) else bcc) or []
        return plugin.send(
            to=to,
            from_=(
                from_
                or kwargs.get('from')
                or (headers or {}).get('from')
                or plugin.account.display_name
                or plugin.account.username
            ),
            cc=cc,
            bcc=bcc,
            subject=subject,
            body=body,
            body_type=body_type,
            attachments=attachments,
            headers=headers,
        )

    @staticmethod
    def _process_account_changes(
        account: str, cur_status: AccountsStatus, new_status: AccountsStatus
    ) -> AccountFolderChanges:
        folders = new_status.get(account) or {}
        mail_flag_changed: Dict[str, Dict[MailFlagType, Dict[int, bool]]] = defaultdict(
            lambda: defaultdict(lambda: defaultdict(bool))
        )

        for folder, folder_status in folders.items():
            for flag, new_mail in folder_status.items():
                cur_mail = (cur_status.get(account) or {}).get(folder, {}).get(flag, {})
                cur_mail_keys = set(map(int, cur_mail.keys()))
                new_mail_keys = set(map(int, new_mail.keys()))
                mail_flag_added_keys = new_mail_keys - cur_mail_keys
                mail_flag_removed_keys = cur_mail_keys - new_mail_keys
                mail_flag_changed[folder][flag].update(
                    {
                        **{msg_id: True for msg_id in mail_flag_added_keys},
                        **{msg_id: False for msg_id in mail_flag_removed_keys},
                    }
                )

        return mail_flag_changed

    def _generate_account_events(
        self, account: str, msgs: Dict[int, Mail], folder_changes: AccountFolderChanges
    ):
        for folder, changes in folder_changes.items():
            for flag, flag_changes in changes.items():
                for msg_id, flag_added in flag_changes.items():
                    msg = msgs.get(msg_id)
                    if not msg:
                        continue

                    if flag == MailFlagType.UNREAD:
                        evt_type = UnseenMailEvent if flag_added else SeenMailEvent
                    elif flag == MailFlagType.FLAGGED:
                        evt_type = (
                            FlaggedMailEvent if flag_added else UnflaggedMailEvent
                        )
                    else:
                        continue

                    self._bus.post(
                        evt_type(
                            account=account,
                            folder=folder,
                            message=msg,
                        )
                    )

    def _generate_events(self, cur_status: AccountsStatus, new_status: AccountsStatus):
        for account in new_status:
            mail_flag_changed = self._process_account_changes(
                account, cur_status, new_status
            )

            msg_ids = {
                msg_id
                for _, changes in mail_flag_changed.items()
                for _, flag_changes in changes.items()
                for msg_id, _ in flag_changes.items()
            }

            if not msg_ids:
                continue

            acc = self._get_account(account)
            if not acc.incoming:
                continue

            msgs = acc.incoming.get_messages(*msg_ids, with_body=False)
            self._generate_account_events(account, msgs, mail_flag_changed)

    def _update_status(self, status: AccountsStatus):
        self._status = status
        with open(self._status_file, 'w') as f:
            status.write(f)

    def loop(self):
        cur_status = self._status.copy()
        new_status = self._check_mailboxes()
        self._generate_events(cur_status, new_status)
        self._update_status(new_status)

    def main(self):
        while not self.should_stop():
            try:
                self.loop()
            except Exception as e:
                self.logger.exception(e)
            finally:
                self.wait_stop(self.poll_interval)


# vim:sw=4:ts=4:et:
