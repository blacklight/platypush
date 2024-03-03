import os
from dataclasses import dataclass, field
from typing import Any, Iterable, Optional
from uuid import UUID, uuid4


class Resource:
    """
    Class to handle resources (files) to be sent through the Telegram API.
    """

    def __init__(
        self,
        file_id: Optional[int] = None,
        url: Optional[str] = None,
        path: Optional[str] = None,
    ):
        assert file_id or url or path, 'You need to specify either file_id, url or path'
        self.file_id = file_id
        self.url = url
        self.path = path
        self.fd = None

    def __enter__(self):
        """
        Context manager to open the file and return the file descriptor.
        """
        if self.path:
            self.fd = open(os.path.abspath(os.path.expanduser(self.path)), 'rb')  # noqa
            return self.fd

        return self.file_id or self.url

    def __exit__(self, *_, **__):
        """
        If the file was opened, close it.
        """
        if self.fd:
            self.fd.close()
            self.fd = None


@dataclass
class Command:
    """
    Dataclass to represent a command to be executed on the Telegram service.
    """

    cmd: str
    args: Iterable = field(default_factory=list)
    kwargs: dict = field(default_factory=dict)
    timeout: Optional[float] = None
    id: UUID = field(default_factory=uuid4)

    def is_end_of_service(self) -> bool:
        """
        Check if a command is the end-of-service command.
        """
        return is_end_of_service(self)


def is_end_of_service(cmd: Any) -> bool:
    """
    Check if a command is the end-of-service command.
    """
    return isinstance(cmd, Command) and cmd.cmd == END_OF_SERVICE.cmd


END_OF_SERVICE = Command('stop')


# vim:sw=4:ts=4:et:
