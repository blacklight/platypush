import datetime
import enum
import os

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    Enum,
    ForeignKey,
)

from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.sql.expression import func

from platypush.backend.http.request import HttpRequest
from platypush.common.db import declarative_base
from platypush.config import Config
from platypush.context import get_plugin
from platypush.message.event.http.rss import NewFeedEvent

Base = declarative_base()
Session = scoped_session(sessionmaker())


class RssUpdates(HttpRequest):
    """
    Gets new items in an RSS feed. You can use this type of object within the context of the
    :class:`platypush.backend.http.poll.HttpPollBackend` backend. Example:

      .. code-block:: yaml

        backend.http.poll:
            requests:
                - type: platypush.backend.http.request.rss.RssUpdates
                  url: https://www.technologyreview.com/feed/
                  title: MIT Technology Review
                  poll_seconds: 86400  # Poll once a day
                  digest_format: html  # Generate an HTML feed with the new items

    Triggers:

        - :class:`platypush.message.event.http.rss.NewFeedEvent` when new items are parsed from a feed or a new digest
          is available.

    Requires:

        * **feedparser** (``pip install feedparser``)

    """

    user_agent = (
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
        + 'Chrome/62.0.3202.94 Safari/537.36'
    )

    def __init__(
        self,
        url,
        title=None,
        headers=None,
        params=None,
        max_entries=None,
        extract_content=False,
        digest_format=None,
        user_agent: str = user_agent,
        body_style: str = 'font-size: 22px; '
        + 'font-family: "Merriweather", Georgia, "Times New Roman", Times, serif;',
        title_style: str = 'margin-top: 30px',
        subtitle_style: str = 'margin-top: 10px; page-break-after: always',
        article_title_style: str = 'page-break-before: always',
        article_link_style: str = 'color: #555; text-decoration: none; border-bottom: 1px dotted',
        article_content_style: str = '',
        *argv,
        **kwargs,
    ):
        """
        :param url: URL to the RSS feed to be monitored.
        :param title: Optional title for the feed.
        :param headers: Extra headers to be passed to the request.
        :param params: Extra GET parameters to be appended to the URL.
        :param max_entries: Maximum number of entries that will be returned in a single
            :class:`platypush.message.event.http.rss.NewFeedEvent` event.
        :param extract_content: Whether the context should also be extracted (through the
            :class:`platypush.plugins.http.webpage.HttpWebpagePlugin` plugin) (default: ``False``).
        :param digest_format: Format of the digest output file (default: None, text. Other supported types: ``html``
            and ``pdf`` (requires the ``weasyprint`` module installed).
        :param user_agent: User agent string to be passed on the request.
        :param body_style: CSS style for the body.
        :param title_style: CSS style for the feed title.
        :param subtitle_style: CSS style for the feed subtitle.
        :param article_title_style: CSS style for the article titles.
        :param article_link_style: CSS style for the article link.
        :param article_content_style: CSS style for the article content.
        """
        self.workdir = os.path.join(os.path.expanduser(Config.get('workdir')), 'feeds')
        self.dbfile = os.path.join(self.workdir, 'rss.db')
        self.url = url
        self.title = title
        self.max_entries = max_entries
        self.user_agent = user_agent
        self.body_style = body_style
        self.title_style = title_style
        self.subtitle_style = subtitle_style
        self.article_title_style = article_title_style
        self.article_link_style = article_link_style
        self.article_content_style = article_content_style

        # If true, then the http.webpage plugin will be used to parse the content
        self.extract_content = extract_content

        self.digest_format = (
            digest_format.lower() if digest_format else None
        )  # Supported formats: html, pdf

        os.makedirs(os.path.expanduser(os.path.dirname(self.dbfile)), exist_ok=True)

        if headers is None:
            headers = {}
        headers['User-Agent'] = self.user_agent

        request_args = {
            'method': 'get',
            'url': self.url,
            'headers': headers,
            'params': params or {},
        }

        super().__init__(skip_first_call=False, args=request_args, *argv, **kwargs)

    def _get_or_create_source(self, session):
        record = session.query(FeedSource).filter_by(url=self.url).first()
        if record is None:
            record = FeedSource(url=self.url, title=self.title)
            session.add(record)

        session.commit()
        return record

    @staticmethod
    def _get_latest_update(session, source_id):
        return (
            session.query(func.max(FeedEntry.published))
            .filter_by(source_id=source_id)
            .scalar()
        )

    def _parse_entry_content(self, link):
        self.logger.info('Extracting content from {}'.format(link))

        parser = get_plugin('http.webpage')
        response = parser.simplify(link)
        output = response.output
        errors = response.errors

        if not output:
            self.logger.warning(
                'Mercury parser error: {}'.format(errors or '[unknown error]')
            )
            return

        return output.get('content')

    def get_new_items(self, response):
        import feedparser

        engine = create_engine(
            'sqlite:///{}'.format(self.dbfile),
            connect_args={'check_same_thread': False},
        )

        Base.metadata.create_all(engine)
        Session.configure(bind=engine)
        self._get_or_create_source(session=Session())

        feed = feedparser.parse(response.text)
        session = Session()
        source_record = self._get_or_create_source(session=session)
        session.add(source_record)
        parse_start_time = datetime.datetime.utcnow()
        entries = []
        latest_update = self._get_latest_update(session, source_record.id)

        if not self.title and 'title' in feed.feed:
            self.title = feed.feed['title']
            source_record.title = self.title

        content = u'''
            <h1 style="{title_style}">{title}</h1>
            <h2 style="{subtitle_style}">Feeds digest generated on {creation_date}</h2>'''.format(
            title_style=self.title_style,
            title=self.title,
            subtitle_style=self.subtitle_style,
            creation_date=datetime.datetime.now().strftime('%d %B %Y, %H:%M'),
        )

        self.logger.info(
            'Parsed {:d} items from RSS feed <{}>'.format(len(feed.entries), self.url)
        )

        for entry in feed.entries:
            if not entry.published_parsed:
                continue

            try:
                entry_timestamp = datetime.datetime(*entry.published_parsed[:6])

                if latest_update is None or entry_timestamp > latest_update:
                    self.logger.info(
                        'Processed new item from RSS feed <{}>'.format(self.url)
                    )
                    entry.summary = entry.summary if hasattr(entry, 'summary') else None

                    if self.extract_content:
                        entry.content = self._parse_entry_content(entry.link)
                    elif hasattr(entry, 'summary'):
                        entry.content = entry.summary
                    else:
                        entry.content = None

                    content += u'''
                        <h1 style="{article_title_style}">
                            <a href="{link}" target="_blank" style="{article_link_style}">{title}</a>
                        </h1>
                        <div class="_parsed-content" style="{article_content_style}">{content}</div>'''.format(
                        article_title_style=self.article_title_style,
                        article_link_style=self.article_link_style,
                        article_content_style=self.article_content_style,
                        link=entry.link,
                        title=entry.title,
                        content=entry.content,
                    )

                    e = {
                        'entry_id': entry.id,
                        'title': entry.title,
                        'link': entry.link,
                        'summary': entry.summary,
                        'content': entry.content,
                        'source_id': source_record.id,
                        'published': entry_timestamp,
                    }

                    entries.append(e)
                    session.add(FeedEntry(**e))
                    if self.max_entries and len(entries) > self.max_entries:
                        break
            except Exception as e:
                self.logger.warning(
                    'Exception encountered while parsing RSS '
                    + f'RSS feed {entry.link}: {e}'
                )
                self.logger.exception(e)

        source_record.last_updated_at = parse_start_time
        digest_filename = None

        if entries:
            self.logger.info(
                'Parsed {} new entries from the RSS feed {}'.format(
                    len(entries), self.title
                )
            )

            if self.digest_format:
                digest_filename = os.path.join(
                    self.workdir,
                    'cache',
                    '{}_{}.{}'.format(
                        datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                        self.title,
                        self.digest_format,
                    ),
                )

                os.makedirs(os.path.dirname(digest_filename), exist_ok=True)

                if self.digest_format == 'html':
                    content = '''
                        <html>
                            <head>
                                <title>{title}</title>
                            </head>
                            <body style="{body_style}">{content}</body>
                        </html>
                    '''.format(
                        title=self.title, body_style=self.body_style, content=content
                    )

                    with open(digest_filename, 'w', encoding='utf-8') as f:
                        f.write(content)
                elif self.digest_format == 'pdf':
                    from weasyprint import HTML, CSS

                    try:
                        from weasyprint.fonts import FontConfiguration
                    except ImportError:
                        from weasyprint.document import FontConfiguration

                    body_style = 'body { ' + self.body_style + ' }'
                    font_config = FontConfiguration()
                    css = [
                        CSS('https://fonts.googleapis.com/css?family=Merriweather'),
                        CSS(string=body_style, font_config=font_config),
                    ]

                    HTML(string=content).write_pdf(digest_filename, stylesheets=css)
                else:
                    raise RuntimeError(
                        f'Unsupported format: {self.digest_format}. Supported formats: html, pdf'
                    )

                digest_entry = FeedDigest(
                    source_id=source_record.id,
                    format=self.digest_format,
                    filename=digest_filename,
                )

                session.add(digest_entry)
                self.logger.info(
                    '{} digest ready: {}'.format(self.digest_format, digest_filename)
                )

        session.commit()
        self.logger.info('Parsing RSS feed {}: completed'.format(self.title))

        return NewFeedEvent(
            request=dict(self),
            response=entries,
            source_id=source_record.id,
            source_title=source_record.title,
            title=self.title,
            digest_format=self.digest_format,
            digest_filename=digest_filename,
        )


class FeedSource(Base):
    """Models the FeedSource table, containing RSS sources to be parsed"""

    __tablename__ = 'FeedSource'
    __table_args__ = {'sqlite_autoincrement': True}

    id = Column(Integer, primary_key=True)
    title = Column(String)
    url = Column(String, unique=True)
    last_updated_at = Column(DateTime)


class FeedEntry(Base):
    """Models the FeedEntry table, which contains RSS entries"""

    __tablename__ = 'FeedEntry'
    __table_args__ = {'sqlite_autoincrement': True}

    id = Column(Integer, primary_key=True)
    entry_id = Column(String)
    source_id = Column(Integer, ForeignKey('FeedSource.id'), nullable=False)
    title = Column(String)
    link = Column(String)
    summary = Column(String)
    content = Column(String)
    published = Column(DateTime)


class FeedDigest(Base):
    """Models the FeedDigest table, containing feed digests either in HTML
    or PDF format"""

    class DigestFormat(enum.Enum):
        html = 1
        pdf = 2

    __tablename__ = 'FeedDigest'
    __table_args__ = {'sqlite_autoincrement': True}

    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey('FeedSource.id'), nullable=False)
    format = Column(Enum(DigestFormat), nullable=False)
    filename = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)


# vim:sw=4:ts=4:et:
