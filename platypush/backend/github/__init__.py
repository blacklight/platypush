import datetime
import os
import threading

from typing import Optional, List

import requests
from sqlalchemy import create_engine, Column, String, DateTime
from sqlalchemy.orm import sessionmaker, scoped_session

from platypush.backend import Backend
from platypush.common.db import declarative_base
from platypush.config import Config
from platypush.message.event.github import (
    GithubPushEvent,
    GithubCommitCommentEvent,
    GithubCreateEvent,
    GithubDeleteEvent,
    GithubEvent,
    GithubForkEvent,
    GithubWikiEvent,
    GithubIssueCommentEvent,
    GithubIssueEvent,
    GithubMemberEvent,
    GithubPublicEvent,
    GithubPullRequestEvent,
    GithubPullRequestReviewCommentEvent,
    GithubReleaseEvent,
    GithubSponsorshipEvent,
    GithubWatchEvent,
)

Base = declarative_base()
Session = scoped_session(sessionmaker())


class GithubResource(Base):
    """
    Models the GithubLastEvent table, containing the timestamp where a certain URL was last checked.
    """

    __tablename__ = 'GithubLastEvent'
    uri = Column(String, primary_key=True)
    last_updated_at = Column(DateTime)


class GithubBackend(Backend):
    """
    This backend monitors for notifications and events either on Github user, organization or repository level.
    You'll need a Github personal access token to use the service. To get one:

        - Access your Github profile settings
        - Select *Developer Settings*
        - Select *Personal access tokens*
        - Click *Generate new token*

    This backend requires the following permissions:

        - ``repo``
        - ``notifications``
        - ``read:org`` if you want to access repositories on organization level.

    Triggers:

        - :class:`platypush.message.event.github.GithubPushEvent` when a new push is created.
        - :class:`platypush.message.event.github.GithubCommitCommentEvent` when a new commit comment is created.
        - :class:`platypush.message.event.github.GithubCreateEvent` when a tag or branch is created.
        - :class:`platypush.message.event.github.GithubDeleteEvent` when a tag or branch is deleted.
        - :class:`platypush.message.event.github.GithubForkEvent` when a user forks a repository.
        - :class:`platypush.message.event.github.GithubWikiEvent` when new activity happens on a repository wiki.
        - :class:`platypush.message.event.github.GithubIssueCommentEvent` when new activity happens on an issue comment.
        - :class:`platypush.message.event.github.GithubIssueEvent` when new repository issue activity happens.
        - :class:`platypush.message.event.github.GithubMemberEvent` when new repository collaborators activity happens.
        - :class:`platypush.message.event.github.GithubPublicEvent` when a repository goes public.
        - :class:`platypush.message.event.github.GithubPullRequestEvent` when new pull request related activity happens.
        - :class:`platypush.message.event.github.GithubPullRequestReviewCommentEvent` when activity happens on a pull
            request commit.
        - :class:`platypush.message.event.github.GithubReleaseEvent` when a new release happens.
        - :class:`platypush.message.event.github.GithubSponsorshipEvent` when new sponsorship related activity happens.
        - :class:`platypush.message.event.github.GithubWatchEvent` when someone stars/starts watching a repository.
        - :class:`platypush.message.event.github.GithubEvent` for any event that doesn't fall in the above categories
            (``event_type`` will be set accordingly).

    """

    _base_url = 'https://api.github.com'

    def __init__(
        self,
        user: str,
        user_token: str,
        repos: Optional[List[str]] = None,
        org: Optional[str] = None,
        poll_seconds: int = 60,
        max_events_per_scan: Optional[int] = 10,
        *args,
        **kwargs
    ):
        """
        If neither ``repos`` nor ``org`` is specified then the backend will monitor all new events on user level.

        :param user: Github username.
        :param user_token: Github personal access token.
        :param repos: List of repos to be monitored - if a list is provided then only these repositories will be
            monitored for events. Repositories should be passed in the format ``username/repository``.
        :param org: Organization to be monitored - if provided then only this organization will be monitored for events.
        :param poll_seconds: How often the backend should check for new events, in seconds (default: 60).
        :param max_events_per_scan: Maximum number of events per resource that will be triggered if there is a large
            number of events/notification since the last check (default: 10). Specify 0 or null for no limit.
        """
        super().__init__(*args, **kwargs)
        self._last_text: Optional[str] = None
        self.user = user
        self.user_token = user_token
        self.repos = repos or []
        self.org = org
        self.poll_seconds = poll_seconds
        self.db_lock = threading.RLock()
        self.workdir = os.path.join(os.path.expanduser(Config.get('workdir')), 'github')
        self.dbfile = os.path.join(self.workdir, 'github.db')
        self.max_events_per_scan = max_events_per_scan

        os.makedirs(os.path.dirname(self.dbfile), exist_ok=True)
        self._init_db()

    def _request(self, uri: str, method: str = 'get') -> dict:
        method = getattr(requests, method.lower())
        return method(
            self._base_url + uri,
            auth=(self.user, self.user_token),
            headers={'Accept': 'application/vnd.github.v3+json'},
        ).json()

    def _init_db(self):
        engine = create_engine(
            'sqlite:///{}'.format(self.dbfile),
            connect_args={'check_same_thread': False},
        )
        Base.metadata.create_all(engine)
        Session.configure(bind=engine)

    @staticmethod
    def _to_datetime(time_string: str) -> datetime.datetime:
        """Convert ISO 8061 string format with leading 'Z' into something understandable by Python"""
        return datetime.datetime.fromisoformat(time_string[:-1] + '+00:00')

    @staticmethod
    def _get_or_create_resource(uri: str, session: Session) -> GithubResource:
        record = session.query(GithubResource).filter_by(uri=uri).first()
        if record is None:
            record = GithubResource(uri=uri)
            session.add(record)
            session.commit()

        return record

    def _get_last_event_time(self, uri: str):
        with self.db_lock:
            record = self._get_or_create_resource(uri=uri, session=Session())
            return (
                record.last_updated_at.replace(tzinfo=datetime.timezone.utc)
                if record.last_updated_at
                else None
            )

    def _update_last_event_time(self, uri: str, last_updated_at: datetime.datetime):
        with self.db_lock:
            session = Session()
            record = self._get_or_create_resource(uri=uri, session=session)
            record.last_updated_at = last_updated_at
            session.add(record)
            session.commit()

    @classmethod
    def _parse_event(cls, event: dict) -> GithubEvent:
        event_mapping = {
            'PushEvent': GithubPushEvent,
            'CommitCommentEvent': GithubCommitCommentEvent,
            'CreateEvent': GithubCreateEvent,
            'DeleteEvent': GithubDeleteEvent,
            'ForkEvent': GithubForkEvent,
            'GollumEvent': GithubWikiEvent,
            'IssueCommentEvent': GithubIssueCommentEvent,
            'IssuesEvent': GithubIssueEvent,
            'MemberEvent': GithubMemberEvent,
            'PublicEvent': GithubPublicEvent,
            'PullRequestEvent': GithubPullRequestEvent,
            'PullRequestReviewCommentEvent': GithubPullRequestReviewCommentEvent,
            'ReleaseEvent': GithubReleaseEvent,
            'SponsorshipEvent': GithubSponsorshipEvent,
            'WatchEvent': GithubWatchEvent,
        }

        event_type = (
            event_mapping[event['type']]
            if event['type'] in event_mapping
            else GithubEvent
        )
        return event_type(
            event_type=event['type'],
            actor=event['actor'],
            repo=event.get('repo', {}),
            payload=event['payload'],
            created_at=cls._to_datetime(event['created_at']),
        )

    def _events_monitor(self, uri: str, method: str = 'get'):
        def thread():
            while not self.should_stop():
                try:
                    events = self._request(uri, method)
                    if not events:
                        continue

                    last_event_time = self._get_last_event_time(uri)
                    new_last_event_time = last_event_time
                    fired_events = []

                    for event in events:
                        if (
                            self.max_events_per_scan
                            and len(fired_events) >= self.max_events_per_scan
                        ):
                            break

                        event_time = self._to_datetime(event['created_at'])
                        if last_event_time and event_time <= last_event_time:
                            break
                        if not new_last_event_time or event_time > new_last_event_time:
                            new_last_event_time = event_time

                        fired_events.append(self._parse_event(event))

                    for event in fired_events:
                        self.bus.post(event)

                    self._update_last_event_time(
                        uri=uri, last_updated_at=new_last_event_time
                    )
                except Exception as e:
                    self.logger.warning(
                        'Encountered exception while fetching events from {}: {}'.format(
                            uri, str(e)
                        )
                    )
                    self.logger.exception(e)

                if self.wait_stop(timeout=self.poll_seconds):
                    break

        return thread

    def run(self):
        self.logger.info('Starting Github backend')
        monitors = []

        if self.repos:
            for repo in self.repos:
                monitors.append(
                    threading.Thread(
                        target=self._events_monitor(
                            '/networks/{repo}/events'.format(repo=repo)
                        )
                    )
                )
        if self.org:
            monitors.append(
                threading.Thread(
                    target=self._events_monitor(
                        '/orgs/{org}/events'.format(org=self.org)
                    )
                )
            )

        if not (self.repos or self.org):
            monitors.append(
                threading.Thread(
                    target=self._events_monitor(
                        '/users/{user}/events'.format(user=self.user)
                    )
                )
            )

        for monitor in monitors:
            monitor.start()

        self.logger.info('Started Github backend')
        for monitor in monitors:
            monitor.join()

        self.logger.info('Github backend terminated')


# vim:sw=4:ts=4:et:
