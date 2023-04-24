import json
import os
import pathlib

from dataclasses import dataclass
from datetime import datetime
from queue import Queue, Empty
from threading import Thread, RLock
from typing import List, Dict, Any, Optional, Tuple

from sqlalchemy import engine, create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, scoped_session

from platypush.backend import Backend
from platypush.common.db import declarative_base
from platypush.config import Config
from platypush.context import get_plugin
from platypush.message.event.mail import (
    MailReceivedEvent,
    MailSeenEvent,
    MailFlaggedEvent,
    MailUnflaggedEvent,
)
from platypush.plugins.mail import MailInPlugin, Mail

# <editor-fold desc="Database tables">
Base = declarative_base()
Session = scoped_session(sessionmaker())


class MailboxStatus(Base):
    """Models the MailboxStatus table, containing information about the state of a monitored mailbox."""

    __tablename__ = 'MailboxStatus'

    mailbox_id = Column(Integer, primary_key=True)
    unseen_message_ids = Column(String, default='[]')
    flagged_message_ids = Column(String, default='[]')
    last_checked_date = Column(DateTime)


# </editor-fold>


# <editor-fold desc="Mailbox model">
@dataclass
class Mailbox:
    plugin: MailInPlugin
    name: str
    args: dict


# </editor-fold>


class MailBackend(Backend):
    """
    This backend can subscribe to one or multiple mail servers and trigger events when new messages are received or
    messages are marked as seen.

    It requires at least one plugin that extends :class:`platypush.plugins.mail.MailInPlugin` (e.g. ``mail.imap``) to
    be installed.

    Triggers:

        - :class:`platypush.message.event.mail.MailReceivedEvent` when a new message is received.
        - :class:`platypush.message.event.mail.MailSeenEvent` when a message is marked as seen.
        - :class:`platypush.message.event.mail.MailFlaggedEvent` when a message is marked as flagged/starred.
        - :class:`platypush.message.event.mail.MailUnflaggedEvent` when a message is marked as unflagged/unstarred.

    """

    def __init__(
        self,
        mailboxes: List[Dict[str, Any]],
        timeout: Optional[int] = 60,
        poll_seconds: Optional[int] = 60,
        **kwargs
    ):
        """
        :param mailboxes: List of mailboxes to be monitored. Each mailbox entry contains a ``plugin`` attribute to
            identify the :class:`platypush.plugins.mail.MailInPlugin` plugin that will be used (e.g. ``mail.imap``)
            and the arguments that will be passed to :meth:`platypush.plugins.mail.MailInPlugin.search_unseen_messages`.
            The ``name`` parameter can be used to identify this mailbox in the relevant events, otherwise
            ``Mailbox #{id}`` will be used as a name. Example configuration:

              .. code-block:: yaml

                 backend.mail:
                     mailboxes:
                         - plugin: mail.imap
                           name: "My Local Server"
                           username: me@mydomain.com
                           password: my-imap-password
                           server: localhost
                           ssl: true
                           folder: "All Mail"

                         - plugin: mail.imap
                           name: "GMail"
                           username: me@gmail.com
                           password: my-google-password
                           server: imap.gmail.com
                           ssl: true
                            folder: "INBOX"

            If you have a default configuration available for a mail plugin you can implicitly reuse it without
            replicating it here. Example:

              .. code-block:: yaml

                 mail.imap:
                     username: me@mydomain.com
                     password: my-imap-password
                     server: localhost
                     ssl: true

                 backend.mail:
                     mailboxes:
                         # The mail.imap default configuration will be used
                         - plugin: mail.imap
                           name: "My Local Server"
                           folder: "All Mail"

        :param poll_seconds: How often the backend should check the mail (default: 60).
        :param timeout: Connect/read timeout for a mailbox, in seconds (default: 60).
        """
        self.logger.info('Initializing mail backend')

        super().__init__(**kwargs)
        self.poll_seconds = poll_seconds
        self.mailboxes: List[Mailbox] = []
        self.timeout = timeout
        self._unread_msgs: List[Dict[int, Mail]] = [{}] * len(mailboxes)
        self._flagged_msgs: List[Dict[int, Mail]] = [{}] * len(mailboxes)
        self._db_lock = RLock()
        self.workdir = os.path.join(os.path.expanduser(Config.get('workdir')), 'mail')
        self.dbfile = os.path.join(self.workdir, 'backend.db')

        # Parse mailboxes
        for i, mbox in enumerate(mailboxes):
            assert (
                'plugin' in mbox
            ), 'No plugin attribute specified for mailbox n.{}'.format(i)
            plugin = get_plugin(mbox.pop('plugin'))
            assert isinstance(plugin, MailInPlugin), '{} is not a MailInPlugin'.format(
                plugin
            )
            name = mbox.pop('name') if 'name' in mbox else 'Mailbox #{}'.format(i + 1)
            self.mailboxes.append(Mailbox(plugin=plugin, name=name, args=mbox))

        # Configure/sync db
        pathlib.Path(self.workdir).mkdir(parents=True, exist_ok=True, mode=0o750)
        self._db = self._db_get_engine()
        Base.metadata.create_all(self._db)
        Session.configure(bind=self._db)
        self._db_load_mailboxes_status()
        self.logger.info('Mail backend initialized')

    # <editor-fold desc="Database methods">
    def _db_get_engine(self) -> engine.Engine:
        return create_engine(
            'sqlite:///{}'.format(self.dbfile),
            connect_args={'check_same_thread': False},
        )

    def _db_load_mailboxes_status(self) -> None:
        mailbox_ids = list(range(len(self.mailboxes)))

        with self._db_lock:
            session = Session()
            records = {
                record.mailbox_id: record
                for record in session.query(MailboxStatus)
                .filter(MailboxStatus.mailbox_id.in_(mailbox_ids))
                .all()
            }

            for mbox_id, _ in enumerate(self.mailboxes):
                if mbox_id not in records:
                    record = MailboxStatus(
                        mailbox_id=mbox_id,
                        unseen_message_ids='[]',
                        flagged_message_ids='[]',
                    )
                    session.add(record)
                else:
                    record = records[mbox_id]

                unseen_msg_ids = json.loads(record.unseen_message_ids or '[]')
                flagged_msg_ids = json.loads(record.flagged_message_ids or '[]')
                self._unread_msgs[mbox_id] = {msg_id: {} for msg_id in unseen_msg_ids}
                self._flagged_msgs[mbox_id] = {msg_id: {} for msg_id in flagged_msg_ids}

            session.commit()

    def _db_get_mailbox_status(
        self, mailbox_ids: List[int]
    ) -> Dict[int, MailboxStatus]:
        with self._db_lock:
            session = Session()
            return {
                record.mailbox_id: record
                for record in session.query(MailboxStatus)
                .filter(MailboxStatus.mailbox_id.in_(mailbox_ids))
                .all()
            }

    # </editor-fold>

    # <editor-fold desc="Parse unread messages logic">
    @staticmethod
    def _check_thread(
        unread_queue: Queue, flagged_queue: Queue, plugin: MailInPlugin, **args
    ):
        def thread():
            # noinspection PyUnresolvedReferences
            unread = plugin.search_unseen_messages(**args).output
            unread_queue.put({msg.id: msg for msg in unread})

            # noinspection PyUnresolvedReferences
            flagged = plugin.search_flagged_messages(**args).output
            flagged_queue.put({msg.id: msg for msg in flagged})

        return thread

    def _get_unread_seen_msgs(
        self, mailbox_idx: int, unread_msgs: Dict[int, Mail]
    ) -> Tuple[Dict[int, Mail], Dict[int, Mail]]:
        prev_unread_msgs = self._unread_msgs[mailbox_idx]

        return {
            msg_id: unread_msgs[msg_id]
            for msg_id in unread_msgs
            if msg_id not in prev_unread_msgs
        }, {
            msg_id: prev_unread_msgs[msg_id]
            for msg_id in prev_unread_msgs
            if msg_id not in unread_msgs
        }

    def _get_flagged_unflagged_msgs(
        self, mailbox_idx: int, flagged_msgs: Dict[int, Mail]
    ) -> Tuple[Dict[int, Mail], Dict[int, Mail]]:
        prev_flagged_msgs = self._flagged_msgs[mailbox_idx]

        return {
            msg_id: flagged_msgs[msg_id]
            for msg_id in flagged_msgs
            if msg_id not in prev_flagged_msgs
        }, {
            msg_id: prev_flagged_msgs[msg_id]
            for msg_id in prev_flagged_msgs
            if msg_id not in flagged_msgs
        }

    def _process_msg_events(
        self,
        mailbox_id: int,
        unread: List[Mail],
        seen: List[Mail],
        flagged: List[Mail],
        unflagged: List[Mail],
        last_checked_date: Optional[datetime] = None,
    ):
        for msg in unread:
            if msg.date and last_checked_date and msg.date < last_checked_date:
                continue
            self.bus.post(
                MailReceivedEvent(mailbox=self.mailboxes[mailbox_id].name, message=msg)
            )

        for msg in seen:
            self.bus.post(
                MailSeenEvent(mailbox=self.mailboxes[mailbox_id].name, message=msg)
            )

        for msg in flagged:
            self.bus.post(
                MailFlaggedEvent(mailbox=self.mailboxes[mailbox_id].name, message=msg)
            )

        for msg in unflagged:
            self.bus.post(
                MailUnflaggedEvent(mailbox=self.mailboxes[mailbox_id].name, message=msg)
            )

    def _check_mailboxes(self) -> List[Tuple[Dict[int, Mail], Dict[int, Mail]]]:
        workers = []
        queues: List[Tuple[Queue, Queue]] = []
        results = []

        for mbox in self.mailboxes:
            unread_queue, flagged_queue = [Queue()] * 2
            worker = Thread(
                target=self._check_thread(
                    unread_queue=unread_queue,
                    flagged_queue=flagged_queue,
                    plugin=mbox.plugin,
                    **mbox.args
                )
            )
            worker.start()
            workers.append(worker)
            queues.append((unread_queue, flagged_queue))

        for worker in workers:
            worker.join(timeout=self.timeout)

        for i, (unread_queue, flagged_queue) in enumerate(queues):
            try:
                unread = unread_queue.get(timeout=self.timeout)
                flagged = flagged_queue.get(timeout=self.timeout)
                results.append((unread, flagged))
            except Empty:
                self.logger.warning(
                    'Checks on mailbox #{} timed out after {} seconds'.format(
                        i + 1, self.timeout
                    )
                )
                continue

        return results

    # </editor-fold>

    # <editor-fold desc="Loop function">
    def loop(self):
        records = []
        mailbox_statuses = self._db_get_mailbox_status(list(range(len(self.mailboxes))))
        results = self._check_mailboxes()

        for i, (unread, flagged) in enumerate(results):
            unread_msgs, seen_msgs = self._get_unread_seen_msgs(i, unread)
            flagged_msgs, unflagged_msgs = self._get_flagged_unflagged_msgs(i, flagged)
            self._process_msg_events(
                i,
                unread=list(unread_msgs.values()),
                seen=list(seen_msgs.values()),
                flagged=list(flagged_msgs.values()),
                unflagged=list(unflagged_msgs.values()),
                last_checked_date=mailbox_statuses[i].last_checked_date,
            )

            self._unread_msgs[i] = unread
            self._flagged_msgs[i] = flagged
            records.append(
                MailboxStatus(
                    mailbox_id=i,
                    unseen_message_ids=json.dumps(list(unread.keys())),
                    flagged_message_ids=json.dumps(list(flagged.keys())),
                    last_checked_date=datetime.now(),
                )
            )

        with self._db_lock:
            session = Session()
            for record in records:
                session.merge(record)
            session.commit()

    # </editor-fold>


# vim:sw=4:ts=4:et:
