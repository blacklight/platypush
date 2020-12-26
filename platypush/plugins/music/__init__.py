from platypush.plugins import Plugin, action


class MusicPlugin(Plugin):
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)

    @action
    def play(self):
        raise NotImplementedError()

    @action
    def pause(self):
        raise NotImplementedError()

    @action
    def stop(self):
        raise NotImplementedError()

    @action
    def next(self):
        raise NotImplementedError()

    @action
    def previous(self):
        raise NotImplementedError()

    @action
    def set_volume(self, volume):
        raise NotImplementedError()

    @action
    def seek(self, position):
        raise NotImplementedError()

    @action
    def add(self, content):
        raise NotImplementedError()

    @action
    def clear(self):
        raise NotImplementedError()

    @action
    def status(self):
        raise NotImplementedError()


# vim:sw=4:ts=4:et:

