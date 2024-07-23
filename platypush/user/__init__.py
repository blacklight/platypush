import base64
import datetime
import enum
import hashlib
import json
import os
import random
import time
from typing import List, Optional, Dict, Tuple, Union

import rsa

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import make_transient

from platypush.common.db import Base
from platypush.config import Config
from platypush.context import get_plugin
from platypush.exceptions.user import (
    InvalidJWTTokenException,
    InvalidCredentialsException,
)
from platypush.utils import get_or_generate_stored_rsa_key_pair, utcnow


class AuthenticationStatus(enum.Enum):
    """
    Enum for authentication errors.
    """

    OK = ''
    INVALID_AUTH_TYPE = 'invalid_auth_type'
    INVALID_CREDENTIALS = 'invalid_credentials'
    INVALID_METHOD = 'invalid_method'
    INVALID_JWT_TOKEN = 'invalid_jwt_token'
    INVALID_OTP_CODE = 'invalid_otp_code'
    MISSING_OTP_CODE = 'missing_otp_code'
    MISSING_PASSWORD = 'missing_password'
    MISSING_USERNAME = 'missing_username'
    PASSWORD_MISMATCH = 'password_mismatch'
    REGISTRATION_DISABLED = 'registration_disabled'
    REGISTRATION_REQUIRED = 'registration_required'


class UserManager:
    """
    Main class for managing platform users
    """

    _otp_workdir = os.path.join(Config.get_workdir(), 'otp')
    _otp_keyfile = os.path.join(_otp_workdir, 'key')
    _otp_keyfile_pub = f'{_otp_keyfile}.pub'

    _jwt_workdir = os.path.join(Config.get_workdir(), 'jwt')
    _jwt_keyfile = os.path.join(_jwt_workdir, 'id_rsa')
    _jwt_keyfile_pub = f'{_jwt_keyfile}.pub'

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

    @classmethod
    def _get_jwt_rsa_key_pair(cls):
        """
        Get or generate the JWT RSA key pair.
        """
        return get_or_generate_stored_rsa_key_pair(cls._jwt_keyfile, size=2048)

    @classmethod
    def _get_or_generate_otp_rsa_key_pair(cls):
        """
        Get or generate the OTP RSA key pair.
        """
        return get_or_generate_stored_rsa_key_pair(cls._otp_keyfile, size=4096)

    @staticmethod
    def _encrypt(data: Union[str, bytes, dict, list, tuple], key: rsa.PublicKey) -> str:
        """
        Encrypt the data using the given RSA public key.
        """
        if isinstance(data, tuple):
            data = list(data)
        if isinstance(data, (dict, list)):
            data = json.dumps(data, sort_keys=True, indent=None)
        if isinstance(data, str):
            data = data.encode('ascii')

        return base64.b64encode(rsa.encrypt(data, key)).decode()

    @staticmethod
    def _decrypt(data: Union[str, bytes], key: rsa.PrivateKey) -> str:
        """
        Decrypt the data using the given RSA private key.
        """
        if isinstance(data, str):
            data = data.encode('ascii')

        return rsa.decrypt(base64.b64decode(data), key).decode()

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

    def create_user(self, username: str, password: str, **kwargs):
        if not username:
            raise ValueError('Invalid or empty username')
        if not password:
            raise ValueError('Please provide a password for the user')

        with self._get_session(locked=True) as session:
            user = self._get_user(session, username)
            if user:
                raise NameError(f'The user {username} already exists')

            password_salt = os.urandom(16)
            hmac_iterations = 100_000
            record = User(
                username=username,
                password=self._encrypt_password(
                    password, password_salt, hmac_iterations
                ),
                password_salt=password_salt.hex(),
                hmac_iterations=hmac_iterations,
                created_at=utcnow(),
                **kwargs,
            )

            session.add(record)
            session.commit()
            user = self._get_user(session, username)

        return self._mask_password(user)

    def update_password(self, username, old_password, new_password, code=None):
        with self._get_session(locked=True) as session:
            if not self._authenticate_user(session, username, old_password, code=code):
                return False

            user = self._get_user(session, username)
            user.password_salt = user.password_salt or os.urandom(16).hex()
            user.hmac_iterations = user.hmac_iterations or 100_000
            salt = bytes.fromhex(user.password_salt)
            user.password = self._encrypt_password(
                new_password, salt, user.hmac_iterations
            )
            session.commit()
            return True

    def authenticate_user(self, username, password, code=None, return_error=False):
        with self._get_session() as session:
            return self._authenticate_user(
                session, username, password, code=code, return_error=return_error
            )

    def authenticate_user_session(self, session_token, with_error=False):
        with self._get_session() as session:
            users_count = session.query(User).count()
            if not users_count:
                return (
                    (None, None, AuthenticationStatus.REGISTRATION_REQUIRED)
                    if with_error
                    else (None, None)
                )

            user_session = (
                session.query(UserSession)
                .filter_by(session_token=session_token)
                .first()
            )

            expires_at = (
                user_session.expires_at.replace(tzinfo=datetime.timezone.utc)
                if user_session and user_session.expires_at
                else None
            )

            if not user_session or (expires_at and expires_at < utcnow()):
                return (
                    (None, None, AuthenticationStatus.INVALID_CREDENTIALS)
                    if with_error
                    else (None, None)
                )

            user = session.query(User).filter_by(user_id=user_session.user_id).first()
            return (
                (self._mask_password(user), user_session, AuthenticationStatus.OK)
                if with_error
                else (
                    self._mask_password(user),
                    user_session,
                )
            )

    def delete_user(self, username):
        with self._get_session(locked=True) as session:
            user = self._get_user(session, username)
            if not user:
                raise NameError(f'No such user: {username}')

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

    def create_user_session(
        self,
        username,
        password,
        code=None,
        expires_at=None,
        error_on_invalid_credentials=False,
    ):
        with self._get_session(locked=True) as session:
            user, status = self._authenticate_user(  # type: ignore
                session,
                username,
                password,
                code=code,
                return_error=error_on_invalid_credentials,
            )

            if not user:
                return None if not error_on_invalid_credentials else (None, status)

            if expires_at:
                if isinstance(expires_at, (int, float)):
                    expires_at = datetime.datetime.fromtimestamp(expires_at)
                elif isinstance(expires_at, str):
                    expires_at = datetime.datetime.fromisoformat(expires_at)

            user_session = UserSession(
                user_id=user.user_id,
                session_token=self.generate_session_token(),
                csrf_token=self.generate_session_token(),
                created_at=utcnow(),
                expires_at=expires_at,
            )

            session.add(user_session)
            session.commit()
            return user_session, (
                AuthenticationStatus.OK if not error_on_invalid_credentials else status
            )

    def create_otp_secret(
        self, username: str, expires_at: Optional[datetime.datetime] = None
    ):
        pubkey, _ = self._get_or_generate_otp_rsa_key_pair()

        # Generate a new OTP secret and encrypt it with the OTP RSA key pair
        otp_secret = "".join(
            random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ234567") for _ in range(32)
        )

        encrypted_secret = self._encrypt(otp_secret, pubkey)

        with self._get_session(locked=True) as session:
            user = self._get_user(session, username)
            assert user, f'No such user: {username}'

            # Create a new OTP secret
            user_otp = UserOtp(
                user_id=user.user_id,
                otp_secret=encrypted_secret,
                created_at=utcnow(),
                expires_at=expires_at,
            )

            # Remove any existing OTP secret and replace it with the new one
            session.query(UserOtp).filter_by(user_id=user.user_id).delete()
            session.add(user_otp)
            session.commit()

        return user_otp

    def get_otp_secret(self, username: str) -> Optional[str]:
        with self._get_session() as session:
            user = self._get_user(session, username)
            if not user:
                return None

            user_otp = session.query(UserOtp).filter_by(user_id=user.user_id).first()
            if not user_otp:
                return None

            _, priv_key = self._get_or_generate_otp_rsa_key_pair()
            return self._decrypt(user_otp.otp_secret, priv_key)

    @staticmethod
    def _get_user(session, username):
        return session.query(User).filter_by(username=username).first()

    @classmethod
    def _encrypt_password(
        cls, pwd: str, salt: Optional[bytes] = None, iterations: Optional[int] = None
    ) -> str:
        # Legacy password check that uses bcrypt if no salt and iterations are provided
        # See https://git.platypush.tech/platypush/platypush/issues/397
        if not (salt and iterations):
            import bcrypt

            return bcrypt.hashpw(pwd.encode(), bcrypt.gensalt(12)).decode()

        return hashlib.pbkdf2_hmac('sha256', pwd.encode(), salt, iterations).hex()

    @classmethod
    def _check_password(
        cls,
        pwd: str,
        hashed_pwd: str,
        salt: Optional[bytes] = None,
        iterations: Optional[int] = None,
    ) -> bool:
        # Legacy password check that uses bcrypt if no salt and iterations are provided
        # See https://git.platypush.tech/platypush/platypush/issues/397
        if not (salt and iterations):
            import bcrypt

            return bcrypt.checkpw(pwd.encode(), hashed_pwd.encode())

        return (
            hashlib.pbkdf2_hmac(
                'sha256',
                pwd.encode(),
                salt,
                iterations,
            ).hex()
            == hashed_pwd
        )

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

        pub_key, _ = self._get_jwt_rsa_key_pair()
        return self._encrypt(
            {
                'username': username,
                'password': password,
                'created_at': datetime.datetime.now().timestamp(),
                'expires_at': expires_at.timestamp() if expires_at else None,
            },
            pub_key,
        )

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
        _, priv_key = self._get_jwt_rsa_key_pair()

        try:
            payload = json.loads(self._decrypt(token, priv_key))
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

    def _authenticate_user(
        self,
        session,
        username: str,
        password: str,
        code: Optional[str] = None,
        return_error: bool = False,
    ) -> Union[Optional['User'], Tuple[Optional['User'], 'AuthenticationStatus']]:
        """
        :return: :class:`platypush.user.User` instance if the user exists and
        the password is valid, ``None`` otherwise.
        """
        user = self._get_user(session, username)

        # The user does not exist
        if not user:
            return (
                None
                if not return_error
                else (None, AuthenticationStatus.INVALID_CREDENTIALS)
            )

        # The password is not correct
        if not self._check_password(
            password,
            user.password,
            bytes.fromhex(user.password_salt) if user.password_salt else None,
            user.hmac_iterations,
        ):
            return (
                None
                if not return_error
                else (None, AuthenticationStatus.INVALID_CREDENTIALS)
            )

        otp_secret = self.get_otp_secret(username)

        # The user doesn't have 2FA enabled and the password is correct:
        # authentication successful
        if not otp_secret:
            return user if not return_error else (user, AuthenticationStatus.OK)

        # The user has 2FA enabled but the code is missing
        if not code:
            return (
                None
                if not return_error
                else (None, AuthenticationStatus.MISSING_OTP_CODE)
            )

        if self.validate_otp_code(username, code):
            return user if not return_error else (user, AuthenticationStatus.OK)

        if not self.validate_backup_code(username, code):
            return (
                None
                if not return_error
                else (None, AuthenticationStatus.INVALID_OTP_CODE)
            )

        return user if not return_error else (user, AuthenticationStatus.OK)

    def refresh_user_backup_codes(self, username: str):
        """
        Refresh the backup codes for a user with 2FA enabled.
        """
        with self._get_session(locked=True) as session:
            user = self._get_user(session, username)
            if not user:
                return False

            session.query(UserBackupCode).filter_by(user_id=user.user_id).delete()
            pub_key, _ = self._get_or_generate_otp_rsa_key_pair()

            for _ in range(10):
                backup_code = "".join(
                    random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ234567") for _ in range(16)
                )

                user_backup_code = UserBackupCode(
                    user_id=user.user_id,
                    code=self._encrypt(backup_code, pub_key),
                    created_at=utcnow(),
                    expires_at=utcnow() + datetime.timedelta(days=30),
                )

                session.add(user_backup_code)

            session.commit()
            return True

    def get_user_backup_codes(self, username: str) -> List['UserBackupCode']:
        with self._get_session() as session:
            user = self._get_user(session, username)
            if not user:
                return []

            _, priv_key = self._get_or_generate_otp_rsa_key_pair()
            codes = session.query(UserBackupCode).filter_by(user_id=user.user_id).all()

            for code in codes:
                code.code = self._decrypt(code.code, priv_key)

            return codes

    def validate_backup_code(self, username: str, code: str) -> bool:
        with self._get_session() as session:
            user = self._get_user(session, username)
            if not user:
                return False

            pub_key, _ = self._get_or_generate_otp_rsa_key_pair()
            user_backup_code = (
                session.query(UserBackupCode)
                .filter_by(user_id=user.user_id, code=self._encrypt(code, pub_key))
                .first()
            )

            if not user_backup_code:
                return False

            session.delete(user_backup_code)
            session.commit()

        return True

    def validate_otp_code(self, username: str, code: str) -> bool:
        otp = get_plugin('otp')
        assert otp

        with self._get_session() as session:
            user = self._get_user(session, username)
            if not user:
                return False

            otp_secret = self.get_otp_secret(username)
            if not otp_secret:
                return False

            _, priv_key = self._get_or_generate_otp_rsa_key_pair()
            otp_secret = self._decrypt(otp_secret, priv_key)

        return otp.verify_time_otp(otp=code, secret=otp_secret)

    def disable_mfa(self, username: str):
        with self._get_session(locked=True) as session:
            user = self._get_user(session, username)
            if not user:
                return False

            session.query(UserOtp).filter_by(user_id=user.user_id).delete()
            session.query(UserBackupCode).filter_by(user_id=user.user_id).delete()
            session.commit()
            return True


class User(Base):
    """Models the User table"""

    __tablename__ = 'user'
    __table_args__ = {'sqlite_autoincrement': True}

    user_id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String)
    password_salt = Column(String)
    hmac_iterations = Column(Integer)
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


class UserOtp(Base):
    """
    Models the UserOtp table, which contains the OTP secrets for each user.
    """

    __tablename__ = 'user_otp'

    user_id = Column(Integer, ForeignKey('user.user_id'), primary_key=True)
    otp_secret = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime)
    expires_at = Column(DateTime)


class UserBackupCode(Base):
    """
    Models the UserBackupCode table, which contains the backup codes for each
    user with 2FA enabled.
    """

    __tablename__ = 'user_backup_code'

    user_id = Column(Integer, ForeignKey('user.user_id'), primary_key=True)
    code = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime)
    expires_at = Column(DateTime)


# vim:sw=4:ts=4:et:
