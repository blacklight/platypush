import enum

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)

from platypush.common.db import Base


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
    INVALID_SESSION = 'invalid_session'
    MISSING_OTP_CODE = 'missing_otp_code'
    MISSING_PASSWORD = 'missing_password'
    MISSING_USERNAME = 'missing_username'
    PASSWORD_MISMATCH = 'password_mismatch'
    REGISTRATION_DISABLED = 'registration_disabled'
    REGISTRATION_REQUIRED = 'registration_required'
    UNKNOWN_ERROR = 'unknown_error'


class User(Base):
    """Models the User table"""

    __tablename__ = 'user'

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String)
    password_salt = Column(String)
    hmac_iterations = Column(Integer)
    created_at = Column(DateTime)


class UserSession(Base):
    """Models the UserSession table"""

    __tablename__ = 'user_session'

    session_id = Column(Integer, primary_key=True, autoincrement=True)
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

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.user_id'))
    code = Column(String, nullable=False)
    created_at = Column(DateTime)
    expires_at = Column(DateTime)

    UniqueConstraint(user_id, code)


class UserToken(Base):
    """Models the UserToken table"""

    __tablename__ = 'user_token'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.user_id'), nullable=False)
    token = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime)
    expires_at = Column(DateTime)

    Index('user_token_user_id_token_idx', user_id, token, unique=True)
    Index('user_token_user_id_name_idx', user_id, name, unique=True)
    Index('user_token_user_id_expires_at_idx', user_id, token, expires_at)


# vim:sw=4:ts=4:et:
