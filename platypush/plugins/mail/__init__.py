import inspect
import os
import subprocess

from abc import ABC
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Union, Any, Dict

from platypush.message import JSONAble
from platypush.plugins import Plugin, action


@dataclass
class ServerInfo:
    server: str
    port: int
    username: Optional[str]
    password: Optional[str]
    ssl: bool
    keyfile: Optional[str]
    certfile: Optional[str]
    access_token: Optional[str]
    oauth_mechanism: Optional[str]
    oauth_vendor: Optional[str]
    timeout: Optional[int]


class Mail(JSONAble):
    def __init__(self, id: int, date: datetime, size: int,
                 from_: Optional[Union[Dict[str, str], List[str]]] = None,
                 to: Optional[Union[Dict[str, str], List[str]]] = None,
                 cc: Optional[Union[Dict[str, str], List[str]]] = None,
                 bcc: Optional[Union[Dict[str, str], List[str]]] = None, subject: str = '',
                 payload: Optional[Any] = None, **kwargs):
        self.id = id
        self.date = date
        self.size = size
        self.from_ = from_ or kwargs.get('from')
        self.to = to
        self.cc = cc or []
        self.bcc = bcc or []
        self.subject = subject
        self.payload = payload

        for k, v in kwargs.items():
            setattr(self, k, v)

    def to_json(self) -> dict:
        return {
            k if k != 'from_' else 'from': v
            for k, v in dict(inspect.getmembers(self)).items()
            if not k.startswith('_') and not callable(v)
        }


class MailPlugin(Plugin, ABC):
    """
    Base class for mail plugins.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.server_info: Optional[ServerInfo] = None

    @staticmethod
    def _get_password(password: Optional[str] = None, password_cmd: Optional[str] = None) -> Optional[str]:
        """
        Get the password either from a provided string or from a password command.
        """
        if not password_cmd:
            return password

        proc = subprocess.Popen(['sh', '-c', password_cmd], stdout=subprocess.PIPE)
        password = proc.communicate()[0].decode()
        return password or None

    @staticmethod
    def _get_path(path: str) -> str:
        return os.path.abspath(os.path.expanduser(path))

    def _get_server_info(self, server: Optional[str] = None, port: Optional[int] = None, username: Optional[str] = None,
                         password: Optional[str] = None, password_cmd: Optional[str] = None,
                         ssl: Optional[bool] = None, keyfile: Optional[str] = None, certfile: Optional[str] = None,
                         access_token: Optional[str] = None, oauth_mechanism: Optional[str] = None,
                         oauth_vendor: Optional[str] = None, default_port: Optional[int] = None,
                         default_ssl_port: Optional[int] = None, timeout: Optional[int] = None, **kwargs) \
            -> ServerInfo:
        if not port:
            port = default_ssl_port if ssl else default_port

        info = ServerInfo(server=server, port=port, username=username,
                          password=self._get_password(password, password_cmd), ssl=ssl, keyfile=keyfile,
                          certfile=certfile, access_token=access_token, oauth_mechanism=oauth_mechanism,
                          oauth_vendor=oauth_vendor, timeout=timeout)

        if server:
            return info

        if self.server_info:
            assert self.server_info.server, 'No server specified'
            return self.server_info

        return info


class MailInPlugin(MailPlugin, ABC):
    """
    Base class for mail in plugins.
    """

    @action
    def get_folders(self) -> list:
        raise NotImplementedError()

    @action
    def get_sub_folders(self) -> list:
        raise NotImplementedError()

    @action
    def search(self, criteria: str, directory: Optional[str] = None) -> list:
        raise NotImplementedError()

    @action
    def search_unseen_messages(self, directory: Optional[str] = None) -> list:
        raise NotImplementedError()

    @action
    def get_message(self, id) -> dict:
        raise NotImplementedError()


# vim:sw=4:ts=4:et:
