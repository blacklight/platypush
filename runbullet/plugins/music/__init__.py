from .. import Plugin

class MusicPlugin(Plugin):
    def run(self, args):
        if 'clear' in args and args['clear']:
            self.clear()

        if 'playlistadd' in args and args['playlistadd']:
            self.playlistadd(args['playlistadd'])

        if 'add' in args and args['add']:
            self.add(args['add'])

        if 'next' in args and args['next']:
            self.next()
        elif 'previous' in args and args['previous']:
            self.previous()

        if 'setvol' in args and args['setvol']:
            self.setvol(args['setvol'])

        status = self.status()
        if 'play' in args and args['play'] and status['state'] != 'play':
            self.play()
        elif 'pause' in args and args['pause'] and status['state'] != 'pause':
            self.pause()
        elif 'stop' in args and args['stop']:
            self.stop()

        return self.status()

    def play(self):
        raise NotImplementedError()

    def pause(self):
        raise NotImplementedError()

    def stop(self):
        raise NotImplementedError()

    def next(self):
        raise NotImplementedError()

    def previous(self):
        raise NotImplementedError()

    def setvol(self, vol):
        raise NotImplementedError()

    def add(self, content):
        raise NotImplementedError()

    def playlistadd(self, playlist):
        raise NotImplementedError()

    def clear(self):
        raise NotImplementedError()

    def status(self):
        raise NotImplementedError()


# vim:sw=4:ts=4:et:

