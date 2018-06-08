import datetime
import enum
import feedparser
import os
import requests
import time

from sqlalchemy import create_engine, Column, Integer, String, DateTime, \
    Enum, UniqueConstraint, ForeignKey

from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.expression import func

from platypush.backend.http.request import HttpRequest
from platypush.config import Config
from platypush.message.event.http.rss import NewFeedEvent

Base = declarative_base()
Session = scoped_session(sessionmaker())


class RssUpdates(HttpRequest):
    """ Gets new items in an RSS feed """

    workdir = os.path.join(os.path.expanduser(Config.get('workdir')), 'feeds')
    dbfile = os.path.join(workdir, 'rss.db')
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'

    def __init__(self, url, title=None, headers=None, params=None, max_entries=None,
                 mercury_api_key=None, digest_format=None, *argv, **kwargs):
        self.url = url
        self.title = title
        self.max_entries = max_entries
        self.mercury_api_key = mercury_api_key  # Mercury Reader API used to parse the content of the link
        self.digest_format = digest_format.lower() if digest_format else None  # Supported formats: html, pdf

        os.makedirs(os.path.expanduser(os.path.dirname(self.dbfile)), exist_ok=True)

        if headers is None: headers = {}
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


    def _get_latest_update(self, session, source_id):
        return session.query(func.max(FeedEntry.published)).filter_by(source_id=source_id).scalar()


    def _parse_entry_content(self, link):
        response = None

        try:
            self.logger.info('Parsing content for {}'.format(link))
            response = requests.get('https://mercury.postlight.com/parser',
                                    params = {'url': link},
                                    headers = {'x-api-key': self.mercury_api_key })
        except Exception as e: self.logger.exception(e)

        return response.json()['content'] if response and response.ok else None


    def get_new_items(self, response):
        engine = create_engine('sqlite:///{}'.format(self.dbfile),
                               connect_args = { 'check_same_thread': False })

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

        digest = u'''
            <h1 style="margin-top: 30px">{}</h1>
            <h2 style="margin-top: 10px; page-break-after: always">
                Feeds digest generated on {} </h2>'''.format(self.title,
                datetime.datetime.now().strftime('%d %B %Y, %H:%M')
            )

        self.logger.info('Parsed {:d} items from RSS feed <{}>'
                     .format(len(feed.entries), self.url))

        for entry in feed.entries:
            if not entry.published_parsed:
                continue

            entry_timestamp = datetime.datetime(*entry.published_parsed[:6])

            if latest_update is None \
                    or entry_timestamp > latest_update:
                self.logger.info('Processed new item from RSS feed <{}>: "{}"'
                             .format(self.url, entry.title))

                entry.summary = entry.summary if hasattr(entry, 'summary') else None

                if self.mercury_api_key:
                    entry.content = self._parse_entry_content(entry.link)
                elif hasattr(entry, 'summary'):
                    entry.content = entry.summary
                else:
                    entry.content = None

                digest += '<h1 style="page-break-before: always">{}</h1>{}' \
                    .format(entry.title, entry.content)

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
                if self.max_entries and len(entries) > self.max_entries: break

        source_record.last_updated_at = parse_start_time
        digest_filename = None

        if entries:
            self.logger.info('Parsed {} new entries from the RSS feed {}'.format(
                len(entries), self.title))

            if self.digest_format:
                digest_filename = os.path.join(self.workdir, 'cache', '{}_{}.{}'.format(
                    datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                    self.title, self.digest_format))

                os.makedirs(os.path.dirname(digest_filename), exist_ok=True)

                if self.digest_format == 'html':
                    with open(digest_filename, 'w', encoding='utf-8') as f:
                        f.write(digest)
                elif self.digest_format == 'pdf':
                    import weasyprint
                    weasyprint.HTML(string=digest).write_pdf(digest_filename)
                else:
                    raise RuntimeError('Unsupported format: {}. Supported formats: ' +
                                    'html or pdf'.format(self.digest_format))

                digest_entry = FeedDigest(source_id=source_record.id,
                                        format=self.digest_format,
                                        filename=digest_filename)

                session.add(digest_entry)
                self.logger.info('{} digest ready: {}'.format(self.digest_format, digest_filename))

        session.commit()
        self.logger.info('Parsing RSS feed {}: completed'.format(self.title))

        return NewFeedEvent(request=dict(self), response=entries,
                            source_id=source_record.id, title=self.title,
                            digest_format=self.digest_format,
                            digest_filename=digest_filename)


class FeedSource(Base):
    """ Models the FeedSource table, containing RSS sources to be parsed """

    __tablename__ = 'FeedSource'
    __table_args__ = ({ 'sqlite_autoincrement': True })

    id = Column(Integer, primary_key=True)
    title = Column(String)
    url = Column(String, unique=True)
    last_updated_at = Column(DateTime)


class FeedEntry(Base):
    """ Models the FeedEntry table, which contains RSS entries """

    __tablename__ = 'FeedEntry'
    __table_args__ = ({ 'sqlite_autoincrement': True })

    id = Column(Integer, primary_key=True)
    entry_id = Column(String)
    source_id = Column(Integer, ForeignKey('FeedSource.id'), nullable=False)
    title = Column(String)
    link = Column(String)
    summary = Column(String)
    content = Column(String)
    published = Column(DateTime)


class FeedDigest(Base):
    """ Models the FeedDigest table, containing feed digests either in HTML
        or PDF format """

    class DigestFormat(enum.Enum):
        html = 1
        pdf = 2

    __tablename__ = 'FeedDigest'
    __table_args__ = ({ 'sqlite_autoincrement': True })

    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey('FeedSource.id'), nullable=False)
    format = Column(Enum(DigestFormat), nullable=False)
    filename = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)


# vim:sw=4:ts=4:et:

