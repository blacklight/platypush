from abc import ABC, abstractmethod
from typing import Dict, Iterable, Optional

from platypush.plugins import Plugin, action


class MusicPlugin(Plugin, ABC):
    """
    Base class for music player plugins.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @action
    @abstractmethod
    def play(self, **kwargs):
        raise NotImplementedError()

    @action
    @abstractmethod
    def pause(self, **kwargs):
        raise NotImplementedError()

    @action
    @abstractmethod
    def stop(self, **kwargs):
        raise NotImplementedError()

    @action
    @abstractmethod
    def next(self, **kwargs):
        raise NotImplementedError()

    @action
    @abstractmethod
    def previous(self, **kwargs):
        raise NotImplementedError()

    @action
    @abstractmethod
    def set_volume(self, volume: float, **kwargs):
        raise NotImplementedError()

    @action
    @abstractmethod
    def volup(self, step: Optional[float] = None, **kwargs):
        raise NotImplementedError()

    @action
    @abstractmethod
    def voldown(self, step: Optional[float] = None, **kwargs):
        raise NotImplementedError()

    @action
    @abstractmethod
    def seek(self, position, **kwargs):
        raise NotImplementedError()

    @action
    @abstractmethod
    def add(self, resource, **kwargs):
        raise NotImplementedError()

    @action
    @abstractmethod
    def clear(self, **kwargs):
        raise NotImplementedError()

    @action
    @abstractmethod
    def status(self, **kwargs):
        raise NotImplementedError()

    @action
    @abstractmethod
    def current_track(self, **kwargs):
        raise NotImplementedError()

    @action
    @abstractmethod
    def get_playlists(self, **kwargs):
        raise NotImplementedError()

    @action
    @abstractmethod
    def get_playlist(self, playlist, **kwargs):
        raise NotImplementedError()

    @action
    @abstractmethod
    def add_to_playlist(self, playlist, resources, **kwargs):
        raise NotImplementedError()

    @action
    @abstractmethod
    def remove_from_playlist(self, playlist, resources, **kwargs):
        raise NotImplementedError()

    @action
    @abstractmethod
    def playlist_move(self, playlist, from_pos: int, to_pos: int, **kwargs):
        raise NotImplementedError()

    @action
    @abstractmethod
    def search(self, query, **kwargs):
        raise NotImplementedError()

    @action
    def get_images(self, resources: Iterable[str], **__) -> Dict[str, Optional[str]]:
        """
        Get the images for a list of URIs.

        .. note:: This is an optional action, and it may not be implemented by all plugins.
                  If the plugin doesn't implement this action, it will return an empty dictionary.

        :param uris: List of URIs.
        :return: Dictionary in the form ``{uri: image_url}``.
        """
        return {}


# vim:sw=4:ts=4:et:
