import base64
import datetime
import hashlib
import json
import os
import random
import time
from typing import List, Optional, Tuple, Union

import rsa
from sqlalchemy import and_, or_
from sqlalchemy.orm import make_transient

from platypush.common.db import Base
from platypush.config import Config
from platypush.context import get_plugin
from platypush.exceptions.user import (
    InvalidCredentialsException,
    InvalidJWTTokenException,
    InvalidTokenException,
    NoUserException,
    OtpRecordAlreadyExistsException,
)
from platypush.utils import get_or_generate_stored_rsa_key_pair, utcnow

from ._model import (
    AuthenticationStatus,
    User,
    UserBackupCode,
    UserOtp,
    UserSession,
    UserToken,
)


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
        return get_or_generate_stored_rsa_key_pair(cls._otp_keyfile, size=2048)

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

    def authenticate_user(
        self, username, password, code=None, skip_2fa=False, with_status=False
    ):
        with self._get_session() as session:
            return self._authenticate_user(
                session,
                username,
                password,
                code=code,
                skip_2fa=skip_2fa,
                with_status=with_status,
            )

    def authenticate_user_session(self, session_token, with_status=False):
        with self._get_session() as session:
            users_count = session.query(User).count()
            if not users_count:
                return (
                    (None, None, AuthenticationStatus.REGISTRATION_REQUIRED)
                    if with_status
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
                    if with_status
                    else (None, None)
                )

            user = session.query(User).filter_by(user_id=user_session.user_id).first()
            return (
                (self._mask_password(user), user_session, AuthenticationStatus.OK)
                if with_status
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
        with_status=False,
    ):
        with self._get_session(locked=True) as session:
            user, status = self._authenticate_user(  # type: ignore
                session,
                username,
                password,
                code=code,
                with_status=with_status,
            )

            if not user:
                return None if not with_status else (None, status)

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
                AuthenticationStatus.OK if not with_status else status
            )

    def create_otp_secret(
        self,
        username: str,
        expires_at: Optional[datetime.datetime] = None,
        otp_secret: Optional[str] = None,
        dry_run: bool = False,
    ):
        # Generate a new OTP secret and encrypt it with the OTP RSA key pair
        otp_secret = otp_secret or "".join(
            random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ234567") for _ in range(32)
        )

        with self._get_session(locked=True) as session:
            user = self._get_user(session, username)
            if not user:
                raise InvalidCredentialsException()

            # Create a new OTP secret
            user_otp = UserOtp(
                user_id=user.user_id,
                otp_secret=otp_secret,
                created_at=utcnow(),
                expires_at=expires_at,
            )

            if not dry_run:
                # Store a copy of the OTP secret encrypted with the RSA public key
                pubkey, _ = self._get_or_generate_otp_rsa_key_pair()
                encrypted_secret = self._encrypt(otp_secret, pubkey)
                encrypted_otp = UserOtp(
                    user_id=user_otp.user_id,
                    otp_secret=encrypted_secret,
                    created_at=user_otp.created_at,
                    expires_at=user_otp.expires_at,
                )

                # Remove any existing OTP secret and replace it with the new one
                session.query(UserOtp).filter_by(user_id=user.user_id).delete()
                session.add(encrypted_otp)
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
        cls,
        pwd: str,
        salt: Optional[Union[str, bytes]] = None,
        iterations: Optional[int] = None,
    ) -> str:
        # Legacy password check that uses bcrypt if no salt and iterations are provided
        # See https://git.platypush.tech/platypush/platypush/issues/397
        if not (salt and iterations):
            import bcrypt

            return bcrypt.hashpw(pwd.encode(), bcrypt.gensalt(12)).decode()

        if isinstance(salt, str):
            salt = bytes.fromhex(salt)

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
        user = self.authenticate_user(username, password, skip_2fa=True)
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

    def validate_jwt_token(self, token: str) -> User:
        """
        Validate a JWT token.

        :param token: Token to validate.
        :return: On success, it returns the user associated to the token.
        :raises: :class:`platypush.exceptions.user.InvalidJWTTokenException` in
            case of invalid token.
        :raises: :class:`platypush.exceptions.user.InvalidCredentialsException`
            in case of invalid credentials stored in the token.
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
            payload.get('username', ''), payload.get('password', ''), skip_2fa=True
        )

        if not user:
            raise InvalidCredentialsException()

        return user

    def _authenticate_user(
        self,
        session,
        username: str,
        password: str,
        code: Optional[str] = None,
        skip_2fa: bool = False,
        with_status: bool = False,
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
                if not with_status
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
                if not with_status
                else (None, AuthenticationStatus.INVALID_CREDENTIALS)
            )

        otp_secret = self.get_otp_secret(username)

        # The user doesn't have 2FA enabled and the password is correct:
        # authentication successful
        if skip_2fa or not otp_secret:
            return user if not with_status else (user, AuthenticationStatus.OK)

        # The user has 2FA enabled but the code is missing
        if not code:
            return (
                None
                if not with_status
                else (None, AuthenticationStatus.MISSING_OTP_CODE)
            )

        # The user has 2FA enabled and a TOTP code is provided
        if self.validate_otp_code(username, code):
            return user if not with_status else (user, AuthenticationStatus.OK)

        # The user has 2FA enabled and a backup code is provided
        if not self.validate_backup_code(username, code):
            return (
                None
                if not with_status
                else (None, AuthenticationStatus.INVALID_OTP_CODE)
            )

        return user if not with_status else (user, AuthenticationStatus.OK)

    def refresh_user_backup_codes(self, username: str) -> List[str]:
        """
        Refresh the backup codes for a user with 2FA enabled.
        """
        backup_codes = [
            "".join(
                random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ234567") for _ in range(16)
            )
            for _ in range(10)
        ]

        with self._get_session(locked=True) as session:
            user = self._get_user(session, username)
            if not user:
                return []

            session.query(UserBackupCode).filter_by(user_id=user.user_id).delete()
            stored_codes = []

            for backup_code in backup_codes:
                encrypted_code = self._encrypt_password(
                    backup_code,
                    salt=user.password_salt,
                    iterations=user.hmac_iterations,
                )

                user_backup_code = UserBackupCode(
                    user_id=user.user_id,
                    code=encrypted_code,
                    created_at=utcnow(),
                    expires_at=utcnow() + datetime.timedelta(days=30),
                )

                session.add(user_backup_code)
                stored_codes.append(backup_code)

            session.commit()
            return stored_codes

    def validate_backup_code(self, username: str, code: str) -> bool:
        with self._get_session() as session:
            user = self._get_user(session, username)
            if not user:
                return False

            encrypted_code = self._encrypt_password(
                code,
                salt=user.password_salt,
                iterations=user.hmac_iterations,
            )

            user_backup_code = (
                session.query(UserBackupCode)
                .filter_by(user_id=user.user_id, code=encrypted_code)
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

        return otp.verify_time_otp(otp=code, secret=otp_secret).output

    def disable_otp(self, username: str):
        with self._get_session(locked=True) as session:
            user = self._get_user(session, username)
            if not user:
                return False

            session.query(UserOtp).filter_by(user_id=user.user_id).delete()
            session.query(UserBackupCode).filter_by(user_id=user.user_id).delete()
            session.commit()
            return True

    def enable_otp(
        self,
        username: str,
        dry_run: bool = False,
        otp_secret: Optional[str] = None,
    ):
        with self._get_session() as session:
            user = self._get_user(session, username)
            if not user:
                raise InvalidCredentialsException()

            user_otp = session.query(UserOtp).filter_by(user_id=user.user_id).first()
            if user_otp:
                raise OtpRecordAlreadyExistsException()

            user_otp = self.create_otp_secret(
                username, otp_secret=otp_secret, dry_run=dry_run
            )

            backup_codes = (
                self.refresh_user_backup_codes(username) if not dry_run else []
            )

            return user_otp, backup_codes

    def generate_api_token(
        self,
        username: str,
        name: Optional[str] = None,
        expires_at: Optional[datetime.datetime] = None,
    ) -> str:
        """
        Create a random API token for a user.

        These are randomly generated tokens stored encrypted in the server's
        database. They are recommended for API usage over JWT tokens because:

            1. JWT tokens rely on the user's password and are invalidated if
               the user changes the password.
            2. JWT tokens are stateless and can't be revoked once generated -
               unless the user changes the password.
            3. They can end up exposing either the user's password, the
               server's keys, or both, if not handled properly.

        :param username: User name.
        :param name: Name of the token (default: ``<username>__<random-string>``).
        :param expires_at: Expiration datetime of the token.
        :return: The generated token as a string.
        :raises: :class:`platypush.exceptions.user.NoUserException` if the user
            does not exist.
        """
        user = self.get_user(username)
        if not user:
            raise NoUserException()

        token = (
            username
            + ':'
            + ''.join(
                random.choice(
                    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789._"
                )
                for _ in range(32)
            )
        )

        name = name or f'{username}__' + ''.join(
            random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ234567") for _ in range(8)
        )

        with self._get_session() as session:
            user_token = UserToken(
                user_id=user.user_id,
                name=name,
                token=self._encrypt_password(
                    token, user.password_salt, user.hmac_iterations
                ),
                created_at=utcnow(),
                expires_at=expires_at,
            )

            session.add(user_token)
            session.commit()

        return token

    @staticmethod
    def _user_by_token(session, token: str) -> Optional[User]:
        username = token.split(':')[0]
        return session.query(User).filter_by(username=username).first()

    def validate_api_token(self, token: str) -> User:
        """
        Validate an API token.

        :param token: Token to validate.
        :return: On success, it returns the user associated to the token.
        :raises: :class:`platypush.exceptions.user.InvalidTokenException` in
            case of invalid token.
        """
        with self._get_session() as session:
            user = self._user_by_token(session, token)
            if not user:
                raise InvalidTokenException()

            encrypted_token = self._encrypt_password(
                token, user.password_salt, user.hmac_iterations  # type: ignore
            )

            user_token = (
                session.query(UserToken)
                .filter(
                    and_(
                        UserToken.token == encrypted_token,
                        UserToken.user_id == user.user_id,
                        or_(
                            UserToken.expires_at.is_(None),
                            UserToken.expires_at >= utcnow(),
                        ),
                    )
                )
                .first()
            )

            if not user_token:
                raise InvalidTokenException()

            return user

    def delete_api_token(
        self,
        username: str,
        token: Optional[str] = None,
        token_id: Optional[int] = None,
    ):
        """
        Delete an API token.

        Either <token> or <token_id> must be provided.

        :param token: Token to delete.
        :param username: User name.
        :param token_id: Token ID.
        :return: True if the token was successfully deleted, False otherwise.
        """
        assert token or token_id, 'Either token or token_id must be provided'

        with self._get_session() as session:
            if token:
                user = self._user_by_token(session, token)
            else:
                user = self._get_user(session, username)

            assert user, 'No such user'

            if token_id:
                user_token = (
                    session.query(UserToken)
                    .filter_by(user_id=user.user_id, id=token_id)
                    .first()
                )
            else:
                encrypted_token = self._encrypt_password(
                    token, user.password_salt, user.hmac_iterations  # type: ignore
                )

                user_token = (
                    session.query(UserToken)
                    .filter_by(
                        token=encrypted_token,
                        user_id=user.user_id,
                    )
                    .first()
                )

            assert user_token, 'No such token'
            session.delete(user_token)
            session.commit()

    def get_api_tokens(self, username: str) -> List[UserToken]:
        """
        Get all the API tokens for a user.

        :param username: User name.
        :return: List of tokens.
        """
        with self._get_session() as session:
            user = self._get_user(session, username)
            if not user:
                return []

            return (
                session.query(UserToken)
                .filter(
                    and_(
                        UserToken.user_id == user.user_id,
                        or_(
                            UserToken.expires_at.is_(None),
                            UserToken.expires_at >= utcnow(),
                        ),
                    )
                )
                .order_by(UserToken.created_at.desc())
                .all()
            )


# vim:sw=4:ts=4:et:
