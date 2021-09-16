import os
from typing import Optional

import pyotp

from platypush import Response
from platypush.config import Config
from platypush.plugins import Plugin, action


class OtpPlugin(Plugin):
    """
    This plugin can be used to generate OTP (One-Time Password) codes compatible with Google Authenticator and
    other 2FA (Two-Factor Authentication) applications.

    Requires:

        * **pyotp** (``pip install pyotp``)
    """

    def __init__(self, secret: Optional[str] = None, secret_path: Optional[str] = None,
                 provisioning_name: Optional[str] = None, issuer_name: Optional[str] = None, **kwargs):
        """
        :param secret: Base32-encoded secret to be used for password generation.
        :param secret_path: If no secret is provided statically, then it will be read from this path
            (default: ``~/.local/share/platypush/otp/secret``). If no secret is found then one will be
            generated.
        :param provisioning_name: If you want to use the Google Authenticator, you can specify the default
            email address to associate to your OTPs for the provisioning process here.
        :param issuer_name: If you want to use the Google Authenticator, you can specify the default
            issuer name to display on your OTPs here.
        """
        super().__init__(**kwargs)
        if not secret_path:
            secret_path = os.path.join(Config.get('workdir'), 'otp', 'secret')

        self.secret_path = secret_path
        self.secret = secret
        self.provisioning_name = provisioning_name
        self.issuer_name = issuer_name

    def _get_secret_from_path(self, secret_path: str) -> str:
        if not os.path.isfile(secret_path):
            secret = self.refresh_secret(secret_path).output
        else:
            with open(secret_path, 'r') as f:
                secret = f.readline()

        return secret

    def _get_secret(self, secret: Optional[str] = None, secret_path: Optional[str] = None) -> str:
        if secret:
            return secret
        if secret_path:
            return self._get_secret_from_path(secret_path)
        if self.secret:
            return self.secret
        if self.secret_path:
            return self._get_secret_from_path(self.secret_path)

        raise AssertionError('No secret nor secret_file specified')

    def _get_topt(self, secret: Optional[str] = None, secret_path: Optional[str] = None) -> pyotp.TOTP:
        return pyotp.TOTP(self._get_secret(secret, secret_path))

    def _get_hopt(self, secret: Optional[str] = None, secret_path: Optional[str] = None) -> pyotp.HOTP:
        return pyotp.HOTP(self._get_secret(secret, secret_path))

    @action
    def refresh_secret(self, secret_path: Optional[str] = None) -> Response:
        """
        Refresh the secret token for key generation given a secret path.

        :param secret_path: Secret path to refresh (default: default configured path).
        """

        secret_path = secret_path or self.secret_path
        assert secret_path, 'No secret_path configured'

        os.makedirs(os.path.dirname(os.path.abspath(os.path.expanduser(secret_path))), exist_ok=True)
        secret = pyotp.random_base32()
        with open(secret_path, 'w') as f:
            f.writelines([secret])    # lgtm [py/clear-text-storage-sensitive-data]
        os.chmod(secret_path, 0o600)
        return secret

    @action
    def get_time_otp(self, secret: Optional[str] = None, secret_path: Optional[str] = None) -> str:
        """
        :param secret: Secret token to be used (overrides configured ``secret``).
        :param secret_path: File containing the secret to be used (overrides configured ``secret_path``).
        :return: A time-based token, as a string.
        """
        otp = self._get_topt(secret, secret_path)
        return otp.now()

    @action
    def get_counter_otp(self, count: int, secret: Optional[str] = None, secret_path: Optional[str] = None) -> str:
        """
        :param count: Index for the counter-OTP.
        :param secret: Secret token to be used (overrides configured ``secret``).
        :param secret_path: File containing the secret to be used (overrides configured ``secret_path``).
        :return: A count-based token, as a string.
        """
        otp = self._get_hopt(secret, secret_path)
        return otp.at(count)

    @action
    def verify_time_otp(self, otp: str, secret: Optional[str] = None, secret_path: Optional[str] = None) -> bool:
        """
        Verify a code against a stored time-OTP.

        :param otp: Code to be verified.
        :param secret: Secret token to be used (overrides configured ``secret``).
        :param secret_path: File containing the secret to be used (overrides configured ``secret_path``).
        :return: True if the code is valid, False otherwise.
        """
        _otp = self._get_topt(secret, secret_path)
        return _otp.verify(otp)

    @action
    def verify_counter_otp(self, otp: str, count: int, secret: Optional[str] = None,
                           secret_path: Optional[str] = None) -> bool:
        """
        Verify a code against a stored counter-OTP.

        :param otp: Code to be verified.
        :param count: Index for the counter-OTP to be verified.
        :param secret: Secret token to be used (overrides configured ``secret``).
        :param secret_path: File containing the secret to be used (overrides configured ``secret_path``).
        :return: True if the code is valid, False otherwise.
        """
        _otp = self._get_hopt(secret, secret_path)
        return _otp.verify(otp, count)

    @action
    def provision_time_otp(self, name: Optional[str] = None, issuer_name: Optional[str] = None,
                           secret: Optional[str] = None, secret_path: Optional[str] = None) -> str:
        """
        Generate a provisioning URI for a time-OTP that can be imported in Google Authenticator.

        :param name: Name or e-mail address associated to the account used by the Google Authenticator.
            If None is specified then the value will be read from the configured ``provisioning_name``.
        :param issuer_name: Name of the issuer of the OTP (default: default configured ``issuer_name`` or None).
        :param secret: Secret token to be used (overrides configured ``secret``).
        :param secret_path: File containing the secret to be used (overrides configured ``secret_path``).
        :return: Generated provisioning URI.
        """
        name = name or self.provisioning_name
        issuer_name = issuer_name or self.issuer_name
        assert name, 'No account name or default provisioning address provided'

        _otp = self._get_topt(secret, secret_path)
        return _otp.provisioning_uri(name, issuer_name=issuer_name)

    @action
    def provision_counter_otp(self, name: Optional[str] = None, issuer_name: Optional[str] = None, initial_count=0,
                              secret: Optional[str] = None, secret_path: Optional[str] = None) -> str:
        """
        Generate a provisioning URI for a counter-OTP that can be imported in Google Authenticator.

        :param name: Name or e-mail address associated to the account used by the Google Authenticator.
            If None is specified then the value will be read from the configured ``provisioning_name``.
        :param issuer_name: Name of the issuer of the OTP (default: default configured ``issuer_name`` or None).
        :param initial_count: Initial value for the counter (default: 0).
        :param secret: Secret token to be used (overrides configured ``secret``).
        :param secret_path: File containing the secret to be used (overrides configured ``secret_path``).
        :return: Generated provisioning URI.
        """
        name = name or self.provisioning_name
        issuer_name = issuer_name or self.issuer_name
        assert name, 'No account name or default provisioning address provided'

        _otp = self._get_hopt(secret, secret_path)
        return _otp.provisioning_uri(name, issuer_name=issuer_name, initial_count=initial_count)


# vim:sw=4:ts=4:et:
