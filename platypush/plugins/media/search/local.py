import datetime
import os
import re
import time

from sqlalchemy import create_engine, func, or_, Column, Integer, String, \
    DateTime, PrimaryKeyConstraint, ForeignKey

from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.expression import func

from platypush.config import Config
from platypush.plugins.media import MediaPlugin
from platypush.plugins.media.search import MediaSearcher

Base = declarative_base()
Session = scoped_session(sessionmaker())

class LocalMediaSearcher(MediaSearcher):
    """
    This class will search for media in the local configured directories. It
    will index the media files for a faster search, it will detect which
    directories have been changed since the last scan and re-index their content
    if needed.

    Requires:

        * **sqlalchemy** (``pip install sqlalchemy``)
    """

    _filename_separators = '[.,_\-@()\[\]\{\}\s\'\"]+'

    def __init__(self, dirs, *args, **kwargs):
        super().__init__()
        self.dirs = dirs
        db_dir = os.path.join(Config.get('workdir'), 'media')
        os.makedirs(db_dir, exist_ok=True)
        self.db_file = os.path.join(db_dir, 'media.db')
        self._db_engine = None

    def _get_db_session(self):
        if not self._db_engine:
            self._db_engine = create_engine(
                'sqlite:///{}'.format(self.db_file),
                connect_args = {'check_same_thread': False})

            Base.metadata.create_all(self._db_engine)
            Session.configure(bind=self._db_engine)

        return Session()

    @staticmethod
    def _get_or_create_dir_entry(session, path):
        record = session.query(MediaDirectory).filter_by(path=path).first()
        if record is None:
            record = MediaDirectory.build(path=path)
            session.add(record)

        session.commit()
        return record

    @classmethod
    def _get_last_modify_time(cls, path, recursive=False):
        return max([os.path.getmtime(p) for p,_,_ in os.walk(path)]) \
            if recursive else os.path.getmtime(path)

    @classmethod
    def _has_directory_changed_since_last_indexing(self, dir_record):
        if not dir_record.last_indexed_at:
            return True

        return datetime.datetime.fromtimestamp(
            self._get_last_modify_time(dir_record.path)) > dir_record.last_indexed_at

    @classmethod
    def _matches_query(cls, filename, query):
        filename = filename.lower()
        query_tokens = [_.lower() for _ in re.split(
            cls._filename_separators, query.strip())]

        for token in query_tokens:
            if token not in filename:
                return False
        return True

    @classmethod
    def _sync_token_records(cls, session, *tokens):
        tokens = list(tokens)
        if not tokens:
            return []

        records = { record.token: record for record in
                   session.query(MediaToken).filter(
                       MediaToken.token.in_(tokens)).all() }

        for token in tokens:
            if token in records:
                continue
            record = MediaToken.build(token=token)
            session.add(record)
            records[token] = record

        session.commit()
        return session.query(MediaToken).filter(
            MediaToken.token.in_(tokens)).all()

    @classmethod
    def _get_file_records(cls, dir_record, session):
        return session.query(MediaFile).filter_by(
            directory_id=dir_record.id).all()

    def scan(self, media_dir, session=None, dir_record=None):
        """
        Scans a media directory and stores the search results in the internal
        SQLite index
        """

        if not session:
            session = self._get_db_session()

        self.logger.info('Indexing directory {}'.format(media_dir))
        index_start_time = time.time()

        if not dir_record:
            dir_record = self._get_or_create_dir_entry(session, media_dir)

        if not os.path.isdir(media_dir):
            self.logger.info('Directory {} is no longer accessible, removing it'.
                             format(media_dir))
            session.query(MediaDirectory) \
                .filter(MediaDirectory.path==media_dir) \
                .delete(synchronize_session='fetch')
            return

        stored_file_records = {
            f.path: f for f in self._get_file_records(dir_record, session) }

        for path, dirs, files in os.walk(media_dir):
            for filename in files:
                filepath = os.path.join(path, filename)

                if filepath in stored_file_records:
                    # stored_file_records will be used to keep track of the
                    # files that have been removed from media_dir. If the file
                    # is still there, don't index it again
                    del stored_file_records[filepath]
                    continue

                if not MediaPlugin._is_video_file(filename) and \
                        not MediaPlugin._is_audio_file(filename):
                    continue

                self.logger.debug('Syncing item {}'.format(filepath))
                tokens = [_.lower() for _ in re.split(self._filename_separators,
                                                      filename.strip())]

                token_records = self._sync_token_records(session, *tokens)
                file_record = MediaFile.build(directory_id=dir_record.id,
                                              path=filepath)

                session.add(file_record)
                session.commit()
                file_record = session.query(MediaFile).filter_by(
                    directory_id=dir_record.id, path=filepath).one()

                for token_record in token_records:
                    file_token = MediaFileToken.build(file_id=file_record.id,
                                                      token_id=token_record.id)
                    session.add(file_token)

        # stored_file_records should now only contain the records of the files
        # that have been removed from the directory
        if stored_file_records:
            self.logger.info(
                'Removing references to {} deleted media items from {}'.format(
                    len(stored_file_records), media_dir))

            session.query(MediaFile).filter(MediaFile.id.in_(
                [ record.id for record in stored_file_records.values() ]
            )).delete(synchronize_session='fetch')

        dir_record.last_indexed_at = datetime.datetime.now()
        self.logger.info('Scanned {} in {} seconds'.format(
            media_dir, int(time.time()-index_start_time)))

        session.commit()

    def search(self, query, **kwargs):
        """
        Searches in the configured media directories given a query. It uses the
        built-in SQLite index if available. If any directory has changed since
        the last scan then it will be indexed again and the up-to-date results
        will be returned.
        """

        session = self._get_db_session()
        results = {}

        for media_dir in self.dirs:
            self.logger.info('Searching {} for "{}"'.format(media_dir, query))
            dir_record = self._get_or_create_dir_entry(session, media_dir)

            if self._has_directory_changed_since_last_indexing(dir_record):
                self.logger.info('{} has changed since last indexing, '.format(
                    media_dir) + 're-indexing')

                self.scan(media_dir, session=session, dir_record=dir_record)

            query_tokens = [_.lower() for _ in re.split(
                self._filename_separators, query.strip())]

            for file_record in session.query(MediaFile.path). \
                    join(MediaFileToken). \
                    join(MediaToken). \
                    filter(MediaToken.token.in_(query_tokens)). \
                    group_by(MediaFile.path). \
                    having(func.count(MediaFileToken.token_id) >= len(query_tokens)):
                if os.path.isfile(file_record.path):
                    results[file_record.path] = {
                        'url': 'file://' + file_record.path,
                        'title': os.path.basename(file_record.path),
                        'size': os.path.getsize(file_record.path)
                    }

        return results.values()


# --- Table definitions

class MediaDirectory(Base):
    """ Models the MediaDirectory table """

    __tablename__ = 'MediaDirectory'
    __table_args__ = ({ 'sqlite_autoincrement': True })

    id = Column(Integer, primary_key=True)
    path = Column(String)
    last_indexed_at = Column(DateTime)

    @classmethod
    def build(cls, path, last_indexed_at=None, id=None):
        record = cls()
        record.id = id
        record.path = path
        record.last_indexed_at = last_indexed_at
        return record


class MediaFile(Base):
    """ Models the MediaFile table """

    __tablename__ = 'MediaFile'
    __table_args__ = ({ 'sqlite_autoincrement': True })

    id = Column(Integer, primary_key=True)
    directory_id = Column(Integer, ForeignKey(
        'MediaDirectory.id', ondelete='CASCADE'), nullable=False)
    path = Column(String, nullable=False, unique=True)
    indexed_at = Column(DateTime)

    @classmethod
    def build(cls, directory_id, path, indexed_at=None, id=None):
        record = cls()
        record.id = id
        record.directory_id = directory_id
        record.path = path
        record.indexed_at = indexed_at or datetime.datetime.now()
        return record


class MediaToken(Base):
    """ Models the MediaToken table """

    __tablename__ = 'MediaToken'
    __table_args__ = ({ 'sqlite_autoincrement': True })

    id = Column(Integer, primary_key=True)
    token = Column(String, nullable=False, unique=True)

    @classmethod
    def build(cls, token, id=None):
        record = cls()
        record.id = id
        record.token = token
        return record


class MediaFileToken(Base):
    """ Models the MediaFileToken table """

    __tablename__ = 'MediaFileToken'

    file_id = Column(Integer, ForeignKey('MediaFile.id', ondelete='CASCADE'),
                     nullable=False)
    token_id = Column(Integer, ForeignKey('MediaToken.id', ondelete='CASCADE'),
                      nullable=False)

    __table_args__ = ( PrimaryKeyConstraint(file_id, token_id), {} )

    @classmethod
    def build(cls, file_id, token_id, id=None):
        record = cls()
        record.id = id
        record.file_id = file_id
        record.token_id = token_id
        return record


# vim:sw=4:ts=4:et:
