from datetime import datetime
from typing import Iterable, Optional

from platypush.message.event import Event


class NewFeedEntryEvent(Event):
    """
    Event triggered when a new (RSS/Atom) feed entry is received.
    """

    def __init__(
        self,
        *,
        feed_url: str,
        url: str,
        title: Optional[str] = None,
        id: Optional[str] = None,
        feed_title: Optional[str] = None,
        published: Optional[datetime] = None,
        summary: Optional[str] = None,
        content: Optional[str] = None,
        author: Optional[str] = None,
        tags: Optional[Iterable[str]] = None,
        **kwargs
    ):
        super().__init__(
            feed_url=feed_url,
            url=url,
            title=title,
            id=id,
            feed_title=feed_title,
            published=published,
            summary=summary,
            content=content,
            author=author,
            tags=tags or [],
            **kwargs
        )
