import datetime
import feedparser
import logging
import os
import requests
import time

from sqlalchemy import create_engine, Column, Integer, String, DateTime, \
    UniqueConstraint, ForeignKey

from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

from platypush.backend.http.request import HttpRequest
from platypush.config import Config
from platypush.message.event.http.rss import NewFeedEvent
from platypush.utils import mkdir_p

Base = declarative_base()
Session = scoped_session(sessionmaker())


class GetRssUpdates(HttpRequest):
    """ Gets new items in an RSS feed """

    dbfile = os.path.join(os.path.expanduser(Config.get('workdir')), 'feeds', 'rss.db')

    def __init__(self, url, headers=None, params=None, dbfile=None,
                 mercury_api_key=None, *args, **kwargs):

        self.url = url
        self.mercury_api_key = mercury_api_key  # Mercury Reader API used to parse the content of the link

        if dbfile: self.dbfile = dbfile
        mkdir_p(os.path.dirname(self.dbfile))

        self.engine = create_engine('sqlite:///{}'.format(self.dbfile))
        Base.metadata.create_all(self.engine)
        Session.configure(bind=self.engine)
        self._get_or_create_source(session=Session())

        request_args = {
            'method': 'get',
            'url': self.url,
            'headers': headers or {},
            'params': params or {},
        }

        super().__init__(*args, skip_first_call=False, args=request_args, **kwargs)


    def _get_or_create_source(self, session):
        record = session.query(FeedSource).filter_by(url=self.url).first()
        if record is None:
            record = FeedSource(url=self.url)
            session.add(record)

        session.commit()
        return record


    def _parse_entry_content(self, link):
        response = None

        try:
            logging.info('Parsing content for {}'.format(link))
            response = requests.get('https://mercury.postlight.com/parser',
                                    params = {'url': link},
                                    headers = {'x-api-key': self.mercury_api_key })
        except Exception as e: logging.exception(e)

        return response.json()['content'] if response and response.ok else None


    def get_new_items(self, response):
        feed = feedparser.parse(response.text)
        session = Session()
        source_record = self._get_or_create_source(session=session)
        session.add(source_record)
        parse_start_time = datetime.datetime.utcnow()
        entries = []

        if source_record.title != feed.feed['title']:
            source_record.title = feed.feed['title']

        for entry in feed.entries:
            entry_timestamp = datetime.datetime(*entry.published_parsed[:6])

            if source_record.last_updated_at is None \
                    or entry_timestamp > source_record.last_updated_at:
                entry.content = self._parse_entry_content(entry.link) \
                    if self.mercury_api_key else None

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

        source_record.last_updated_at = parse_start_time
        session.commit()

        if entries:
            logging.info('Parsed {} new entries from the RSS feed {}'.format(
                len(entries), source_record.title))

        return NewFeedEvent(dict(self), entries)


class FeedSource(Base):
    __tablename__ = 'FeedSource'
    __table_args__ = ({ 'sqlite_autoincrement': True })

    id = Column(Integer, primary_key=True)
    title = Column(String)
    url = Column(String, unique=True)
    last_updated_at = Column(DateTime)


class FeedEntry(Base):
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


# vim:sw=4:ts=4:et:

