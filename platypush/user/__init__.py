import datetime
import hashlib
import random

import bcrypt

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

from platypush.context import get_plugin

Base = declarative_base()


class UserManager:
    """
    Main class for managing platform users
    """

    # noinspection PyProtectedMember
    def __init__(self):
        db_plugin = get_plugin('db')
        if not db_plugin:
            raise ModuleNotFoundError('Please enable/configure the db plugin for multi-user support')

        self._engine = db_plugin._get_engine()

    def get_user(self, username):
        session = self._get_db_session()
        user = self._get_user(session, username)
        if not user:
            return None

        # Hide password
        user.password = None
        return user

    def get_user_count(self):
        session = self._get_db_session()
        return session.query(User).count()

    def get_users(self):
        session = self._get_db_session()
        return session.query(User)

    def create_user(self, username, password, **kwargs):
        session = self._get_db_session()
        if not username:
            raise ValueError('Invalid or empty username')
        if not password:
            raise ValueError('Please provide a password for the user')

        user = self._get_user(session, username)
        if user:
            raise NameError('The user {} already exists'.format(username))

        record = User(username=username, password=self._encrypt_password(password),
                      created_at=datetime.datetime.utcnow(), **kwargs)

        session.add(record)
        session.commit()
        user = self._get_user(session, username)

        # Hide password
        user.password = None
        return user

    def update_password(self, username, old_password, new_password):
        session = self._get_db_session()
        if not self._authenticate_user(session, username, old_password):
            return False

        user = self._get_user(session, username)
        user.password = self._encrypt_password(new_password)
        session.commit()
        return True

    def authenticate_user(self, username, password):
        session = self._get_db_session()
        return self._authenticate_user(session, username, password)

    def authenticate_user_session(self, session_token):
        session = self._get_db_session()
        user_session = session.query(UserSession).filter_by(session_token=session_token).first()

        if not user_session or (
                user_session.expires_at and user_session.expires_at < datetime.datetime.utcnow()):
            return None, None

        user = session.query(User).filter_by(user_id=user_session.user_id).first()

        # Hide password
        user.password = None
        return user, session

    def delete_user(self, username):
        session = self._get_db_session()
        user = self._get_user(session, username)
        if not user:
            raise NameError('No such user: {}'.format(username))

        user_sessions = session.query(UserSession).filter_by(user_id=user.user_id).all()
        for user_session in user_sessions:
            session.delete(user_session)

        session.delete(user)
        session.commit()
        return True

    def delete_user_session(self, session_token):
        session = self._get_db_session()
        user_session = session.query(UserSession).filter_by(session_token=session_token).first()

        if not user_session:
            return False

        session.delete(user_session)
        session.commit()
        return True

    def create_user_session(self, username, password, expires_at=None):
        session = self._get_db_session()
        if not self._authenticate_user(session, username, password):
            return None

        if expires_at:
            if isinstance(expires_at, int) or isinstance(expires_at, float):
                expires_at = datetime.datetime.fromtimestamp(expires_at)
            elif isinstance(expires_at, str):
                expires_at = datetime.datetime.fromisoformat(expires_at)

        user = self._get_user(session, username)
        user_session = UserSession(user_id=user.user_id, session_token=self._generate_token(),
                                   csrf_token=self._generate_token(), created_at=datetime.datetime.utcnow(),
                                   expires_at=expires_at)

        session.add(user_session)
        session.commit()
        return user_session

    @staticmethod
    def _get_user(session, username):
        return session.query(User).filter_by(username=username).first()

    @staticmethod
    def _encrypt_password(pwd):
        return bcrypt.hashpw(pwd.encode(), bcrypt.gensalt(12))

    @staticmethod
    def _check_password(pwd, hashed_pwd):
        return bcrypt.checkpw(pwd.encode(), hashed_pwd)

    @staticmethod
    def _generate_token():
        rand = bytes(random.randint(0, 255) for _ in range(0, 255))
        return hashlib.sha256(rand).hexdigest()

    def _get_db_session(self):
        Base.metadata.create_all(self._engine)
        session = scoped_session(sessionmaker())
        session.configure(bind=self._engine)
        return session()

    def _authenticate_user(self, session, username, password):
        user = self._get_user(session, username)
        if not user:
            return False

        return self._check_password(password, user.password)


class User(Base):
    """ Models the User table """

    __tablename__ = 'user'
    __table_args__ = ({'sqlite_autoincrement': True})

    user_id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String)
    created_at = Column(DateTime)


class UserSession(Base):
    """ Models the UserSession table """

    __tablename__ = 'user_session'
    __table_args__ = ({'sqlite_autoincrement': True})

    session_id = Column(Integer, primary_key=True)
    session_token = Column(String, unique=True, nullable=False)
    csrf_token = Column(String, unique=True)
    user_id = Column(Integer, ForeignKey('user.user_id'), nullable=False)
    created_at = Column(DateTime)
    expires_at = Column(DateTime)


# vim:sw=4:ts=4:et:
