from datetime import datetime
from dataclasses import dataclass
from typing import Optional, Dict

from platypush.message.event import Event


@dataclass
class Actor:
    id: str
    login: str
    display_login: str
    url: str
    gravatar_id: str
    avatar_url: str


@dataclass
class Repo:
    id: str
    name: str
    url: str


class GithubEvent(Event):
    """ Generic Github event """

    def __init__(self,
                 event_type: str,
                 created_at: datetime,
                 actor: Optional[Dict[str, str]] = None,
                 repo: Optional[Dict[str, str]] = None,
                 *args, **kwargs):
        super().__init__(*args, actor=actor, event_type=event_type, repo=repo, created_at=created_at, **kwargs)
        self.event_type = event_type
        self.actor = Actor(**actor) if actor else None
        self.repo = Repo(**repo) if repo else None
        self.created_at = created_at


class GithubPushEvent(GithubEvent):
    """ Github push event. """

    def __init__(self, payload: dict, *args, **kwargs):
        super().__init__(*args, payload=payload, **kwargs)


class GithubCommitCommentEvent(GithubEvent):
    """ A commit comment is created. """

    def __init__(self, payload: dict, *args, **kwargs):
        super().__init__(*args, payload=payload, **kwargs)


class GithubCreateEvent(GithubEvent):
    """ A git branch or tag is created. """

    def __init__(self, payload: dict, *args, **kwargs):
        super().__init__(*args, payload=payload, **kwargs)


class GithubDeleteEvent(GithubEvent):
    """ A git branch or tag is deleted. """

    def __init__(self, payload: dict, *args, **kwargs):
        super().__init__(*args, payload=payload, **kwargs)


class GithubForkEvent(GithubEvent):
    """ A user forks a watched repository. """

    def __init__(self, payload: dict, *args, **kwargs):
        super().__init__(*args, payload=payload, **kwargs)


class GithubWikiEvent(GithubEvent):
    """ A wiki page is created or updated on a watched repository. """

    def __init__(self, payload: dict, *args, **kwargs):
        super().__init__(*args, payload=payload, **kwargs)


class GithubIssueCommentEvent(GithubEvent):
    """ A comment is added or updated on an issue. """

    def __init__(self, payload: dict, *args, **kwargs):
        super().__init__(*args, payload=payload, **kwargs)


class GithubIssueEvent(GithubEvent):
    """ A new activity is registered on an issue. """

    def __init__(self, payload: dict, *args, **kwargs):
        super().__init__(*args, payload=payload, **kwargs)


class GithubMemberEvent(GithubEvent):
    """ New activity related to repository collaborators. """

    def __init__(self, payload: dict, *args, **kwargs):
        super().__init__(*args, payload=payload, **kwargs)


class GithubPublicEvent(GithubEvent):
    """ A private repository is made public. """

    def __init__(self, payload: dict, *args, **kwargs):
        super().__init__(*args, payload=payload, **kwargs)


class GithubPullRequestEvent(GithubEvent):
    """ New activity related to a pull request. """

    def __init__(self, payload: dict, *args, **kwargs):
        super().__init__(*args, payload=payload, **kwargs)


class GithubPullRequestReviewCommentEvent(GithubEvent):
    """ New activity related to comments of a pull request. """

    def __init__(self, payload: dict, *args, **kwargs):
        super().__init__(*args, payload=payload, **kwargs)


class GithubReleaseEvent(GithubEvent):
    """ New activity related to the release of a repository. """

    def __init__(self, payload: dict, *args, **kwargs):
        super().__init__(*args, payload=payload, **kwargs)


class GithubSponsorshipEvent(GithubEvent):
    """ New activity related to the sponsorship of a repository. """

    def __init__(self, payload: dict, *args, **kwargs):
        super().__init__(*args, payload=payload, **kwargs)


class GithubWatchEvent(GithubEvent):
    """ Event triggered when someone stars or starts watching a repository. """

    def __init__(self, payload: dict, *args, **kwargs):
        super().__init__(*args, payload=payload, **kwargs)


# vim:sw=4:ts=4:et:
