from dataclasses import dataclass, field
import datetime
import enum
from typing import List, Optional

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey

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
    MISSING_OTP_CODE = 'missing_otp_code'
    MISSING_PASSWORD = 'missing_password'
    MISSING_USERNAME = 'missing_username'
    PASSWORD_MISMATCH = 'password_mismatch'
    REGISTRATION_DISABLED = 'registration_disabled'
    REGISTRATION_REQUIRED = 'registration_required'


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


@dataclass
class UserResponse:
    """
    Dataclass containing full information about a user (minus the password).
    """

    user_id: int
    username: str
    otp_secret: Optional[str] = None
    session_token: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    backup_codes: List[str] = field(default_factory=list)


# vim:sw=4:ts=4:et:
