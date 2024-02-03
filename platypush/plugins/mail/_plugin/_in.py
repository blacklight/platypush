from abc import ABC, abstractmethod
from typing import Dict, Iterable, List, Union

from .._model import Mail
from ._base import BaseMailPlugin


class MailInPlugin(BaseMailPlugin, ABC):
    """
    Base class for mail in plugins.
    """

    @abstractmethod
    def get_folders(self, **_) -> list:
        raise NotImplementedError()

    @abstractmethod
    def get_sub_folders(self, **_) -> list:
        raise NotImplementedError()

    @abstractmethod
    def search(
        self, criteria: Union[str, Iterable[str]], folder: str, **_
    ) -> List[Mail]:
        raise NotImplementedError()

    @abstractmethod
    def search_unseen_messages(self, folder: str) -> List[Mail]:
        raise NotImplementedError()

    @abstractmethod
    def search_flagged_messages(self, folder: str, **_) -> List[Mail]:
        raise NotImplementedError()

    @abstractmethod
    def search_starred_messages(self, folder: str, **_) -> List[Mail]:
        raise NotImplementedError()

    @abstractmethod
    def sort(
        self,
        folder: str,
        sort_criteria: Union[str, Iterable[str]],
        criteria: Union[str, Iterable[str]],
    ) -> list:
        raise NotImplementedError()

    @abstractmethod
    def get_messages(self, *ids, with_body: bool = True, **_) -> Dict[int, Mail]:
        raise NotImplementedError()

    def get_message(
        self, id, with_body: bool = True, **_  # pylint: disable=redefined-builtin
    ) -> Mail:
        msgs = self.get_messages(id, with_body=with_body)
        msg = msgs.get(id)
        assert msg, f"Message {id} not found"
        return msg

    @abstractmethod
    def create_folder(self, folder: str, **_):
        raise NotImplementedError()

    @abstractmethod
    def rename_folder(self, old_name: str, new_name: str, **_):
        raise NotImplementedError()

    @abstractmethod
    def delete_folder(self, folder: str, **_):
        raise NotImplementedError()

    @abstractmethod
    def add_flags(
        self, messages: list, flags: Union[str, Iterable[str]], folder: str, **_
    ):
        raise NotImplementedError()

    @abstractmethod
    def set_flags(
        self, messages: list, flags: Union[str, Iterable[str]], folder: str, **_
    ):
        raise NotImplementedError()

    @abstractmethod
    def remove_flags(
        self, messages: list, flags: Union[str, Iterable[str]], folder: str, **_
    ):
        raise NotImplementedError()

    @abstractmethod
    def delete_messages(self, messages: list, folder: str, **_):
        raise NotImplementedError()

    @abstractmethod
    def restore_messages(self, messages: list, folder: str, **_):
        raise NotImplementedError()

    @abstractmethod
    def copy_messages(self, messages: list, dest_folder: str, source_folder: str, **_):
        raise NotImplementedError()

    @abstractmethod
    def move_messages(self, messages: list, dest_folder: str, source_folder: str, **_):
        raise NotImplementedError()

    @abstractmethod
    def expunge_messages(self, folder: str, messages: list, **_):
        raise NotImplementedError()

    @abstractmethod
    def flag_messages(self, messages: list, folder: str, **_):
        raise NotImplementedError()

    @abstractmethod
    def unflag_messages(self, messages: List[int], folder: str = 'INBOX', **_):
        raise NotImplementedError()

    def flag_message(self, message: int, folder: str, **_):
        return self.flag_messages([message], folder=folder)

    def unflag_message(self, message: int, folder: str, **_):
        return self.unflag_messages([message], folder=folder)


# vim:sw=4:ts=4:et:
