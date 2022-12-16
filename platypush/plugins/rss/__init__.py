import datetime
import os
import queue
import re
import threading
import time

from dateutil.tz import tzutc
from typing import Iterable, Optional, Collection, Set
from xml.etree import ElementTree

import dateutil.parser
import requests

from platypush.context import get_bus, get_plugin
from platypush.message.event.rss import NewFeedEntryEvent
from platypush.plugins import RunnablePlugin, action
from platypush.schemas.rss import RssFeedEntrySchema


class RssPlugin(RunnablePlugin):
    """
    A plugin for parsing and subscribing to RSS feeds.

    Triggers:

        - :class:`platypush.message.event.rss.NewFeedEntryEvent` when a new entry is received on a subscribed feed.

    Requires:

        * **feedparser** (``pip install feedparser``)
        * **defusedxml** (``pip install defusedxml``)

    """

    user_agent = (
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
        + 'Chrome/62.0.3202.94 Safari/537.36'
    )

    def __init__(
        self,
        subscriptions: Optional[Collection[str]] = None,
        poll_seconds: int = 300,
        user_agent: str = user_agent,
        **kwargs,
    ):
        """
        :param subscriptions: List of feeds to monitor for updates, as URLs.
            OPML URLs/local files are also supported.
        :param poll_seconds: How often we should check for updates (default: 300 seconds).
        :param user_agent: Custom user agent to use for the requests.
        """
        super().__init__(**kwargs)
        self.poll_seconds = poll_seconds
        self.user_agent = user_agent
        self._feeds_metadata = {}
        self._feed_worker_queues = [queue.Queue()] * 5
        self._feed_response_queue = queue.Queue()
        self._feed_workers = []
        self._latest_entries = []

        self.subscriptions = list(self._parse_subscriptions(subscriptions or []))

        self._latest_timestamps = self._get_latest_timestamps()

    @staticmethod
    def _get_feed_latest_timestamp_varname(url: str) -> str:
        return f'LATEST_FEED_TIMESTAMP[{url}]'

    @classmethod
    def _get_feed_latest_timestamp(cls, url: str) -> Optional[datetime.datetime]:
        t = (
            get_plugin('variable')
            .get(cls._get_feed_latest_timestamp_varname(url))
            .output.get(cls._get_feed_latest_timestamp_varname(url))
        )

        if t:
            return dateutil.parser.isoparse(t)

    def _get_latest_timestamps(self) -> dict:
        return {url: self._get_feed_latest_timestamp(url) for url in self.subscriptions}

    def _update_latest_timestamps(self) -> None:
        variable = get_plugin('variable')
        variable.set(
            **{
                self._get_feed_latest_timestamp_varname(url): latest_timestamp
                for url, latest_timestamp in self._latest_timestamps.items()
            }
        )

    @staticmethod
    def _parse_content(entry) -> Optional[str]:
        content = getattr(entry, 'content', None)
        if not content:
            return

        if isinstance(content, list):
            return content[0]['value']

        return content

    @action
    def parse_feed(self, url: str):
        """
        Parse a feed URL.

        :param url: Feed URL.
        :return: .. schema:: rss.RssFeedEntrySchema(many=True)
        """
        import feedparser

        feed = feedparser.parse(
            requests.get(url, headers={'User-Agent': self.user_agent}).text
        )
        return RssFeedEntrySchema().dump(
            sorted(
                [
                    {
                        'feed_url': url,
                        'feed_title': getattr(feed.feed, 'title', None),
                        'id': getattr(entry, 'id', None),
                        'url': entry.link,
                        'published': datetime.datetime.fromtimestamp(
                            time.mktime(entry.published_parsed)
                        ),
                        'title': entry.title,
                        'summary': getattr(entry, 'summary', None),
                        'content': self._parse_content(entry),
                        'author': getattr(entry, 'author', None),
                        'tags': [
                            tag['term']
                            for tag in getattr(entry, 'tags', [])
                            if tag.get('term')
                        ],
                    }
                    for entry in feed.entries
                    if getattr(entry, 'published_parsed', None)
                ],
                key=lambda e: e['published'],
            ),
            many=True,
        )

    @action
    def get_latest_entries(self, limit: int = 20):
        """
        Get the latest entries from the subscribed feeds, sorted by descending published date.

        :param limit: Maximum number of entries to return (default: 20).
        :return: .. schema:: rss.RssFeedEntrySchema(many=True)
        """
        return sorted(self._latest_entries, key=lambda e: e['published'], reverse=True)[
            :limit
        ]

    def _feed_worker(self, q: queue.Queue):
        while not self.should_stop():
            try:
                url = q.get(block=True, timeout=1)
            except queue.Empty:
                continue

            try:
                self._feed_response_queue.put(
                    {
                        'url': url,
                        'content': self.parse_feed(url).output,
                    }
                )
            except Exception as e:
                self._feed_response_queue.put(
                    {
                        'url': url,
                        'error': e,
                    }
                )

        self._feed_response_queue.put(None)

    def _parse_opml_lists(self, subs: Iterable[str]) -> Set[str]:
        from defusedxml import ElementTree

        feeds = set()
        subs = set(subs)
        content_by_sub = {}
        urls = {sub for sub in subs if re.search(r'^https?://', sub)}
        files = {os.path.expanduser(sub) for sub in subs if sub not in urls}

        for url in urls:
            try:
                content_by_sub[url] = requests.get(
                    url,
                    headers={
                        'User-Agent': self.user_agent,
                    },
                ).text
            except Exception as e:
                self.logger.warning('Could not retrieve subscription %s: %s', url, e)

        for file in files:
            try:
                with open(file, 'r') as f:
                    content_by_sub[file] = f.read()
            except Exception as e:
                self.logger.warning('Could not open file %s: %s', file, e)

        for sub, content in content_by_sub.items():
            root = ElementTree.fromstring(content.strip())
            if root.tag != 'opml':
                self.logger.warning('%s is not a valid OPML resource', sub)
                continue

            feeds.update(self._parse_feeds_from_outlines(root.findall('body/outline')))

        return feeds

    def _parse_feeds_from_outlines(
        self,
        outlines: Iterable[ElementTree.Element],
    ) -> Set[str]:
        feeds = set()
        outlines = list(outlines)

        while outlines:
            outline = outlines.pop(0)
            if 'xmlUrl' in outline.attrib:
                url = outline.attrib['xmlUrl']
                feeds.add(url)
                self._feeds_metadata[url] = {
                    **self._feeds_metadata.get(url, {}),
                    'title': outline.attrib.get('title'),
                    'description': outline.attrib.get('text'),
                    'url': outline.attrib.get('htmlUrl'),
                }

            for i, child in enumerate(outline.iter()):
                if i > 0:
                    outlines.append(child)

        return feeds

    def _parse_subscriptions(self, subs: Iterable[str]) -> Iterable[str]:
        import feedparser

        self.logger.info('Parsing feed subscriptions')
        feeds = set()
        lists = set()

        for sub in subs:
            try:
                # Check if it's an OPML list of feeds or an individual feed
                feed = feedparser.parse(sub)
                if feed.feed.get('opml'):
                    lists.add(sub)
                else:
                    channel = feed.get('channel', {})
                    self._feeds_metadata[sub] = {
                        **self._feeds_metadata.get(sub, {}),
                        'title': channel.get('title'),
                        'description': channel.get('description'),
                        'url': channel.get('link'),
                    }

                    feeds.add(sub)
            except Exception as e:
                self.logger.warning('Could not parse %s: %s', sub, e)

        feeds.update(self._parse_opml_lists(lists))
        return feeds

    @staticmethod
    def _datetime_to_string(dt: datetime.datetime) -> str:
        return dt.replace(tzinfo=tzutc()).strftime('%a, %d %b %Y %H:%M:%S %Z')

    @action
    def export_to_opml(self) -> str:
        """
        Export the list of subscriptions into OPML format.

        :return: The list of subscriptions as a string in OPML format.
        """
        root = ElementTree.Element('opml', {'version': '2.0'})

        head = ElementTree.Element('head')
        title = ElementTree.Element('title')
        title.text = 'Platypush feed subscriptions'
        created = ElementTree.Element('dateCreated')
        created.text = self._datetime_to_string(datetime.datetime.utcnow())
        head.append(title)
        head.append(created)

        body = ElementTree.Element('body')
        feeds = ElementTree.Element('outline', {'text': 'Feeds'})

        for sub in self.subscriptions:
            metadata = self._feeds_metadata.get(sub, {})
            feed = ElementTree.Element(
                'outline',
                {
                    'xmlUrl': sub,
                    'text': metadata.get('description', metadata.get('title', sub)),
                    **({'htmlUrl': metadata['url']} if metadata.get('url') else {}),
                    **({'title': metadata['title']} if metadata.get('title') else {}),
                },
            )

            feeds.append(feed)

        body.append(feeds)

        root.append(head)
        root.append(body)
        return ElementTree.tostring(root, encoding='utf-8', method='xml').decode()

    def main(self):
        self._feed_workers = [
            threading.Thread(target=self._feed_worker, args=(q,))
            for q in self._feed_worker_queues
        ]

        for worker in self._feed_workers:
            worker.start()

        self.logger.info(
            f'Initialized RSS plugin with {len(self.subscriptions)} subscriptions'
        )

        while not self.should_stop():
            responses = {}
            for i, url in enumerate(self.subscriptions):
                worker_queue = self._feed_worker_queues[
                    i % len(self._feed_worker_queues)
                ]
                worker_queue.put(url)

            time_start = time.time()
            timeout = 60
            max_time = time_start + timeout
            new_entries = []

            while (
                not self.should_stop()
                and len(responses) < len(self.subscriptions)
                and time.time() - time_start <= timeout
            ):
                try:
                    response = self._feed_response_queue.get(
                        block=True, timeout=max_time - time_start
                    )
                except queue.Empty:
                    self.logger.warning('RSS parse timeout')
                    break

                if not response:
                    continue

                url = response['url']
                error = response.get('error')
                if error:
                    self.logger.error(f'Could not parse feed {url}: {error}')
                    responses[url] = error
                else:
                    responses[url] = response['content']

            responses = {
                k: v for k, v in responses.items() if not isinstance(v, Exception)
            }

            for url, response in responses.items():
                latest_timestamp = self._latest_timestamps.get(url)
                new_entries += response

                for entry in response:
                    published = datetime.datetime.fromisoformat(entry['published'])
                    if not latest_timestamp or published > latest_timestamp:
                        latest_timestamp = published
                        get_bus().post(NewFeedEntryEvent(**entry))

                self._latest_timestamps[url] = latest_timestamp

            self._update_latest_timestamps()
            self._latest_entries = new_entries
            self.wait_stop(self.poll_seconds)

    def stop(self):
        super().stop()
        for worker in self._feed_workers:
            worker.join(timeout=60)

        self.logger.info('RSS integration stopped')


# vim:sw=4:ts=4:et:
