import base64
import datetime
import hashlib
import json
import random
import time
from typing import Optional, Dict

import bcrypt
import rsa

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import make_transient

from platypush.common.db import Base
from platypush.context import get_plugin
from platypush.exceptions.user import (
    InvalidJWTTokenException,
    InvalidCredentialsException,
)
from platypush.utils import get_or_generate_jwt_rsa_key_pair


class UserManager:
    """
    Main class for managing platform users
    """

    def __init__(self):
        db_plugin = get_plugin('db')
        assert db_plugin, 'Database plugin not configured'
        self.db = db_plugin
        self.db.create_all(self.db.get_engine(), Base)

    @staticmethod
    def _mask_password(user):
        make_transient(user)
        user.password = None
        return user

    def _get_session(self, *args, **kwargs):
        return self.db.get_session(self.db.get_engine(), *args, **kwargs)

    def get_user(self, username):
        with self._get_session() as session:
            user = self._get_user(session, username)
            if not user:
                return None

            session.expunge(user)
            return self._mask_password(user)

    def get_user_count(self):
        with self._get_session() as session:
            return session.query(User).count()

    def get_users(self):
        with self._get_session() as session:
            return session.query(User).all()

    def create_user(self, username, password, **kwargs):
        if not username:
            raise ValueError('Invalid or empty username')
        if not password:
            raise ValueError('Please provide a password for the user')

        with self._get_session(locked=True) as session:
            user = self._get_user(session, username)
            if user:
                raise NameError('The user {} already exists'.format(username))

            record = User(
                username=username,
                password=self._encrypt_password(password),
                created_at=datetime.datetime.utcnow(),
                **kwargs,
            )

            session.add(record)
            session.commit()
            user = self._get_user(session, username)

        return self._mask_password(user)

    def update_password(self, username, old_password, new_password):
        with self._get_session(locked=True) as session:
            if not self._authenticate_user(session, username, old_password):
                return False

            user = self._get_user(session, username)
            user.password = self._encrypt_password(new_password)
            session.commit()
            return True

    def authenticate_user(self, username, password):
        with self._get_session() as session:
            return self._authenticate_user(session, username, password)

    def authenticate_user_session(self, session_token):
        with self._get_session() as session:
            user_session = (
                session.query(UserSession)
                .filter_by(session_token=session_token)
                .first()
            )

            if not user_session or (
                user_session.expires_at
                and user_session.expires_at < datetime.datetime.utcnow()
            ):
                return None, None

            user = session.query(User).filter_by(user_id=user_session.user_id).first()
            return self._mask_password(user), user_session

    def delete_user(self, username):
        with self._get_session(locked=True) as session:
            user = self._get_user(session, username)
            if not user:
                raise NameError('No such user: {}'.format(username))

            user_sessions = (
                session.query(UserSession).filter_by(user_id=user.user_id).all()
            )
            for user_session in user_sessions:
                session.delete(user_session)

            session.delete(user)
            session.commit()
            return True

    def delete_user_session(self, session_token):
        with self._get_session(locked=True) as session:
            user_session = (
                session.query(UserSession)
                .filter_by(session_token=session_token)
                .first()
            )

            if not user_session:
                return False

            session.delete(user_session)
            session.commit()
            return True

    def create_user_session(self, username, password, expires_at=None):
        with self._get_session(locked=True) as session:
            user = self._authenticate_user(session, username, password)
            if not user:
                return None

            if expires_at:
                if isinstance(expires_at, (int, float)):
                    expires_at = datetime.datetime.fromtimestamp(expires_at)
                elif isinstance(expires_at, str):
                    expires_at = datetime.datetime.fromisoformat(expires_at)

            user_session = UserSession(
                user_id=user.user_id,
                session_token=self.generate_session_token(),
                csrf_token=self.generate_session_token(),
                created_at=datetime.datetime.utcnow(),
                expires_at=expires_at,
            )

            session.add(user_session)
            session.commit()
            return user_session

    @staticmethod
    def _get_user(session, username):
        return session.query(User).filter_by(username=username).first()

    @staticmethod
    def _encrypt_password(pwd):
        if isinstance(pwd, str):
            pwd = pwd.encode()
        return bcrypt.hashpw(pwd, bcrypt.gensalt(12)).decode()

    @classmethod
    def _check_password(cls, pwd, hashed_pwd):
        return bcrypt.checkpw(cls._to_bytes(pwd), cls._to_bytes(hashed_pwd))

    @staticmethod
    def _to_bytes(data) -> bytes:
        if isinstance(data, str):
            data = data.encode()
        return data

    @staticmethod
    def generate_session_token():
        rand = bytes(random.randint(0, 255) for _ in range(0, 255))
        return hashlib.sha256(rand).hexdigest()

    def get_user_by_session(self, session_token: str):
        """
        Get a user associated to a session token.

        :param session_token: Session token.
        """
        with self._get_session() as session:
            return (
                session.query(User)
                .join(UserSession)
                .filter_by(session_token=session_token)
                .first()
            )

    def generate_jwt_token(
        self,
        username: str,
        password: str,
        expires_at: Optional[datetime.datetime] = None,
    ) -> str:
        """
        Create a user JWT token for API usage.

        :param username: User name.
        :param password: Password.
        :param expires_at: Expiration datetime of the token.
        :return: The generated JWT token as a string.
        :raises: :class:`platypush.exceptions.user.InvalidCredentialsException` in case of invalid credentials.
        """
        user = self.authenticate_user(username, password)
        if not user:
            raise InvalidCredentialsException()

        pub_key, _ = get_or_generate_jwt_rsa_key_pair()
        payload = json.dumps(
            {
                'username': username,
                'password': password,
                'created_at': datetime.datetime.now().timestamp(),
                'expires_at': expires_at.timestamp() if expires_at else None,
            },
            sort_keys=True,
            indent=None,
        )

        return base64.b64encode(rsa.encrypt(payload.encode('ascii'), pub_key)).decode()

    def validate_jwt_token(self, token: str) -> Dict[str, str]:
        """
        Validate a JWT token.

        :param token: Token to validate.
        :return: On success, it returns the JWT payload with the following structure:

            .. code-block:: json

                {
                    "username": "user ID/name",
                    "created_at": "token creation timestamp",
                    "expires_at": "token expiration timestamp"
                }

        :raises: :class:`platypush.exceptions.user.InvalidJWTTokenException` in case of invalid token.
        """
        _, priv_key = get_or_generate_jwt_rsa_key_pair()

        try:
            payload = json.loads(
                rsa.decrypt(base64.b64decode(token.encode('ascii')), priv_key).decode(
                    'ascii'
                )
            )
        except (TypeError, ValueError) as e:
            raise InvalidJWTTokenException(f'Could not decode JWT token: {e}') from e

        expires_at = payload.get('expires_at')
        if expires_at and time.time() > expires_at:
            raise InvalidJWTTokenException('Expired JWT token')

        user = self.authenticate_user(
            payload.get('username', ''), payload.get('password', '')
        )

        if not user:
            raise InvalidCredentialsException()

        return payload

    def _authenticate_user(self, session, username, password):
        """
        :return: :class:`platypush.user.User` instance if the user exists and the password is valid, ``None`` otherwise.
        """
        user = self._get_user(session, username)
        if not user:
            return None

        if not self._check_password(password, user.password):
            return None

        return user


class User(Base):
    """Models the User table"""

    __tablename__ = 'user'
    __table_args__ = {'sqlite_autoincrement': True}

    user_id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String)
    created_at = Column(DateTime)


class UserSession(Base):
    """Models the UserSession table"""

    __tablename__ = 'user_session'
    __table_args__ = {'sqlite_autoincrement': True}

    session_id = Column(Integer, primary_key=True)
    session_token = Column(String, unique=True, nullable=False)
    csrf_token = Column(String, unique=True)
    user_id = Column(Integer, ForeignKey('user.user_id'), nullable=False)
    created_at = Column(DateTime)
    expires_at = Column(DateTime)


# vim:sw=4:ts=4:et:
