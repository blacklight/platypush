from platypush.plugins import Plugin, action


class MusicPlugin(Plugin):
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)

    @action
    def play(self, **kwargs):
        raise NotImplementedError()

    @action
    def pause(self, **kwargs):
        raise NotImplementedError()

    @action
    def stop(self, **kwargs):
        raise NotImplementedError()

    @action
    def next(self, **kwargs):
        raise NotImplementedError()

    @action
    def previous(self, **kwargs):
        raise NotImplementedError()

    @action
    def set_volume(self, volume, **kwargs):
        raise NotImplementedError()

    @action
    def volup(self, delta, **kwargs):
        raise NotImplementedError()

    @action
    def voldown(self, delta, **kwargs):
        raise NotImplementedError()

    @action
    def seek(self, position, **kwargs):
        raise NotImplementedError()

    @action
    def add(self, resource, **kwargs):
        raise NotImplementedError()

    @action
    def clear(self, **kwargs):
        raise NotImplementedError()

    @action
    def status(self, **kwargs):
        raise NotImplementedError()

    @action
    def current_track(self, **kwargs):
        raise NotImplementedError()

    @action
    def get_playlists(self, **kwargs):
        raise NotImplementedError()

    @action
    def get_playlist(self, playlist, **kwargs):
        raise NotImplementedError()

    @action
    def add_to_playlist(self, playlist, resources, **kwargs):
        raise NotImplementedError()

    @action
    def remove_from_playlist(self, playlist, resources, **kwargs):
        raise NotImplementedError()

    @action
    def playlist_move(self, playlist, from_pos: int, to_pos: int, **kwargs):
        raise NotImplementedError()

    @action
    def search(self, query, *args, **kwargs):
        raise NotImplementedError()


# vim:sw=4:ts=4:et:
