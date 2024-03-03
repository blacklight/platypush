import subprocess

from dataclasses import dataclass
from typing import Optional


@dataclass
class AccountConfig:
    """
    Model for a mail account configuration.
    """

    username: str
    password: Optional[str] = None
    password_cmd: Optional[str] = None
    access_token: Optional[str] = None
    oauth_mechanism: Optional[str] = None
    oauth_vendor: Optional[str] = None
    display_name: Optional[str] = None

    def __post_init__(self):
        """
        Ensure that at least one of password, password_cmd or access_token is provided.
        """
        assert (
            self.password or self.password_cmd or self.access_token
        ), 'No password, password_cmd or access_token provided'

    def get_password(self) -> str:
        """
        Get the password either from a provided string or from a password command.
        """
        if self.password_cmd:
            with subprocess.Popen(
                ['sh', '-c', self.password_cmd], stdout=subprocess.PIPE
            ) as proc:
                return proc.communicate()[0].decode()

        assert self.password, 'No password provided'
        return self.password


# vim:sw=4:ts=4:et:
