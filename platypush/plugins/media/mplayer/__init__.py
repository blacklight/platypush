import os
import re
import select
import subprocess
import threading
import time

from platypush.context import get_bus
from platypush.message.response import Response
from platypush.plugins.media import PlayerState, MediaPlugin
from platypush.message.event.media import MediaPlayEvent, MediaPlayRequestEvent, \
    MediaPauseEvent, MediaStopEvent, NewPlayingMediaEvent

from platypush.plugins import action
from platypush.utils import find_bins_in_path


class MediaMplayerPlugin(MediaPlugin):
    """
    Plugin to control MPlayer instances

    Requires:

        * **mplayer** executable on your system
    """

    _mplayer_default_communicate_timeout = 0.5

    _mplayer_bin_default_args = ['-slave', '-quiet', '-idle', '-input',
                                 'nodefault-bindings', '-noconfig', 'all']

    def __init__(self, mplayer_bin=None,
                 mplayer_timeout=_mplayer_default_communicate_timeout,
                 args=None, *argv, **kwargs):
        """
        Create the MPlayer wrapper. Note that the plugin methods are populated
        dynamically by introspecting the mplayer executable. You can verify the
        supported methods at runtime by using the `list_actions` method.

        :param mplayer_bin: Path to the MPlayer executable (default: search for
            the first occurrence in your system PATH environment variable)
        :type mplayer_bin: str

        :param mplayer_timeout: Timeout in seconds to wait for more data
            from MPlayer before considering a response ready (default: 0.5 seconds)
        :type mplayer_timeout: float

        :param subtitles: Path to the subtitles file
        :type subtitles: str

        :param args: Default arguments that will be passed to the MPlayer
            executable
        :type args: list
        """

        super().__init__(*argv, **kwargs)

        self.args = args or []
        self._init_mplayer_bin(mplayer_bin=mplayer_bin)
        self._build_actions()
        self._player = None
        self._mplayer_timeout = mplayer_timeout
        self._mplayer_stopped_event = threading.Event()
        self._status_lock = threading.Lock()

    def _init_mplayer_bin(self, mplayer_bin=None):
        if not mplayer_bin:
            bin_name = 'mplayer.exe' if os.name == 'nt' else 'mplayer'
            bins = find_bins_in_path(bin_name)

            if not bins:
                raise RuntimeError('MPlayer executable not specified and not ' +
                                   'found in your PATH. Make sure that mplayer' +
                                   'is either installed or configured')

            self.mplayer_bin = bins[0]
        else:
            mplayer_bin = os.path.expanduser(mplayer_bin)
            if not (os.path.isfile(mplayer_bin)
                    and (os.name == 'nt' or os.access(mplayer_bin, os.X_OK))):
                raise RuntimeError('{} is does not exist or is not a valid ' +
                                   'executable file'.format(mplayer_bin))

            self.mplayer_bin = mplayer_bin

    def _init_mplayer(self, mplayer_args=None):
        if self._player:
            try:
                self._player.terminate()
            except Exception as e:
                self.logger.debug('Failed to quit mplayer before _exec: {}'.
                                  format(str(e)))

        mplayer_args = mplayer_args or []
        args = [self.mplayer_bin] + self._mplayer_bin_default_args
        for arg in self.args + mplayer_args:
            if arg not in args:
                args.append(arg)

        popen_args = {
            'stdin': subprocess.PIPE,
            'stdout': subprocess.PIPE,
        }

        if self._env:
            popen_args['env'] = self._env

        self._player = subprocess.Popen(args, **popen_args)
        threading.Thread(target=self._process_monitor()).start()

    def _build_actions(self):
        """ Populates the actions list by introspecting the mplayer executable """

        self._actions = {}
        mplayer = subprocess.Popen([self.mplayer_bin, '-input', 'cmdlist'],
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE)

        def args_pprint(txt):
            lc = txt.lower()
            if lc[0] == '[':
                return '%s=None' % lc[1:-1]
            return lc

        while True:
            line = mplayer.stdout.readline()
            if not line:
                break
            line = line.decode()
            if line[0].isupper():
                continue
            args = line.split()
            cmd_name = args.pop(0)
            arguments = ', '.join([args_pprint(a) for a in args])
            self._actions[cmd_name] = '{}({})'.format(cmd_name, arguments)

    def _exec(self, cmd, *args, mplayer_args=None, prefix=None,
              wait_for_response=False):
        cmd_name = cmd
        response = None

        if cmd_name == 'loadfile' or cmd_name == 'loadlist':
            self._init_mplayer(mplayer_args)
        else:
            if not self._player:
                self.logger.warning('MPlayer is not running')

        cmd = '{}{}{}{}\n'.format(
            prefix + ' ' if prefix else '',
            cmd_name, ' ' if args else '',
            ' '.join(repr(a) for a in args)).encode()

        if not self._player:
            self.logger.warning('Cannot send command {}: player unavailable'.format(cmd))
            return

        self._player.stdin.write(cmd)
        self._player.stdin.flush()

        if cmd_name == 'loadfile' or cmd_name == 'loadlist':
            self._post_event(NewPlayingMediaEvent, resource=args[0])
        elif cmd_name == 'pause':
            self._post_event(MediaPauseEvent)
        elif cmd_name == 'quit' or cmd_name == 'stop':
            if cmd_name == 'quit':
                self._player.terminate()
                self._player.wait()
                try:
                    self._player.kill()
                except Exception:
                    pass
                self._player = None

        if not wait_for_response:
            return

        poll = select.poll()
        poll.register(self._player.stdout, select.POLLIN)
        last_read_time = time.time()

        while time.time() - last_read_time < self._mplayer_timeout:
            result = poll.poll(0)
            if result:
                if not self._player:
                    break

                line = self._player.stdout.readline().decode()
                last_read_time = time.time()

                if line.startswith('ANS_'):
                    m = re.match('^([^=]+)=(.*)$', line[4:])
                    k, v = m.group(1), m.group(2)
                    v = v.strip()
                    if v == 'yes':
                        v = True
                    elif v == 'no':
                        v = False

                    try:
                        v = eval(v)
                    except Exception:
                        pass

                    response = {k: v}

        return response

    @action
    def execute(self, cmd, args=None):
        """
        Execute a raw MPlayer command. See
        https://www.mplayerhq.hu/DOCS/tech/slave.txt for a reference or call
        :meth:`platypush.plugins.media.mplayer.list_actions` to get a list
        """

        args = args or []
        return self._exec(cmd, *args)

    @action
    def list_actions(self):
        return [{'action': a, 'args': self._actions[a]}
                for a in sorted(self._actions.keys())]

    def _process_monitor(self):
        def _thread():
            if not self._player:
                return

            self._mplayer_stopped_event.clear()
            self._player.wait()
            try:
                self.quit()
            except Exception:
                pass

            self._post_event(MediaStopEvent)
            self._mplayer_stopped_event.set()
            self._player = None

        return _thread

    @staticmethod
    def _post_event(evt_type, **evt):
        bus = get_bus()
        bus.post(evt_type(player='local', plugin='media.mplayer', **evt))

    @action
    def play(self, resource, subtitles=None, mplayer_args=None):
        """
        Play a resource.

        :param resource: Resource to play - can be a local file or a remote URL
        :type resource: str

        :param subtitles: Path to optional subtitle file
        :type subtitles: str

        :param mplayer_args: Extra runtime arguments that will be passed to the
            MPlayer executable
        :type mplayer_args: list[str]
        """

        self._post_event(MediaPlayRequestEvent, resource=resource)
        if subtitles:
            mplayer_args = mplayer_args or []
            mplayer_args += ['-sub', self.get_subtitles_file(subtitles)]

        resource = self._get_resource(resource)
        if resource.startswith('file://'):
            resource = resource[7:]

        self._exec('loadfile', resource, mplayer_args=mplayer_args)
        self._post_event(MediaPlayEvent, resource=resource)

        if self.volume:
            self.set_volume(volume=self.volume)

        return self.status()

    @action
    def pause(self):
        """ Toggle the paused state """
        self._exec('pause')
        self._post_event(MediaPauseEvent)
        return self.status()

    @action
    def stop(self):
        """ Stop the playback """
        # return self._exec('stop')
        self.quit()
        return self.status()

    @action
    def quit(self):
        """ Quit the player """
        self._exec('quit')
        self._post_event(MediaStopEvent)
        return self.status()

    @action
    def voldown(self, step=10.0):
        """ Volume down by (default: 10)% """
        self._exec('volume', -step * 10)
        return self.status()

    @action
    def volup(self, step=10.0):
        """ Volume up by (default: 10)% """
        self._exec('volume', step * 10)
        return self.status()

    @action
    def back(self, offset=30.0):
        """ Back by (default: 30) seconds """
        self.step_property('time_pos', -offset)
        return self.status()

    @action
    def forward(self, offset=30.0):
        """ Forward by (default: 30) seconds """
        self.step_property('time_pos', offset)
        return self.status()

    @action
    def toggle_subtitles(self):
        """ Toggle the subtitles visibility """
        subs = self.get_property('sub_visibility').output.get('sub_visibility')
        self._exec('sub_visibility', int(not subs))
        return self.status()

    @action
    def add_subtitles(self, filename, **__):
        """ Sets media subtitles from filename """
        self._exec('sub_visibility', 1)
        self._exec('sub_load', filename)
        return self.status()

    @action
    def remove_subtitles(self, index=None):
        """ Removes the subtitle specified by the index (default: all) """
        if index is None:
            self._exec('sub_remove')
        else:
            self._exec('sub_remove', index)

        return self.status()

    @action
    def is_playing(self):
        """
        :returns: True if it's playing, False otherwise
        """
        return self.get_property('pause').output.get('pause') is False

    @action
    def load(self, resource, mplayer_args=None, **kwargs):
        """
        Load a resource/video in the player.
        """
        if mplayer_args is None:
            mplayer_args = {}
        return self.play(resource, mplayer_args=mplayer_args)

    @action
    def mute(self):
        """ Toggle mute state """
        self._exec('mute')
        return self.status()

    @action
    def seek(self, position):
        """
        Seek backward/forward by the specified number of seconds

        :param position: Number of seconds relative to the current cursor
        :type position: int
        """
        self.step_property('time_pos', position)
        return self.status()

    @action
    def set_position(self, position):
        """
        Seek backward/forward to the specified absolute position

        :param position: Number of seconds from the start
        :type position: int
        """
        self.set_property('time_pos', position)
        return self.status()

    @action
    def set_volume(self, volume):
        """
        Set the volume

        :param volume: Volume value between 0 and 100
        :type volume: float
        """
        self._exec('volume', volume)
        return self.status()

    @action
    def status(self):
        """
        Get the current player state.

        :returns: A dictionary containing the current state.

        Example::

            output = {
                "state": "play"  # or "stop" or "pause"
            }
        """

        if not self._player:
            return {'state': PlayerState.STOP.value}

        status = {}
        props = {
            'duration': 'length',
            'filename': 'filename',
            'fullscreen': 'fullscreen',
            'mute': 'mute',
            'name': 'filename',
            'path': 'path',
            'pause': 'pause',
            'percent_pos': 'percent_pos',
            'position': 'time_pos',
            'title': 'filename',
            'volume': 'volume',
        }

        with self._status_lock:
            for prop, player_prop in props.items():
                value = self.get_property(player_prop).output
                if value is not None:
                    status[prop] = value.get(player_prop)

        status['seekable'] = True if status['duration'] is not None else False
        status['state'] = PlayerState.PAUSE.value if status['pause'] else PlayerState.PLAY.value

        if status['path']:
            status['url'] = ('file://' if os.path.isfile(status['path']) else '') + status['path']

        status['volume_max'] = 100
        return status

    @action
    def get_property(self, property, args=None):
        """
        Get a player property (e.g. pause, fullscreen etc.). See
        https://www.mplayerhq.hu/DOCS/tech/slave.txt for a full list of the
        available properties
        """

        args = args or []
        response = Response(output={})

        result = self._exec('get_property', property, prefix='pausing_keep_force',
                            wait_for_response=True, *args) or {}

        for k, v in result.items():
            if k == 'ERROR' and v not in response.errors:
                response.errors.append('{}{}: {}'.format(property, args, v))
            else:
                response.output[k] = v

        return response

    @action
    def set_property(self, property, value, args=None):
        """
        Set a player property (e.g. pause, fullscreen etc.). See
        https://www.mplayerhq.hu/DOCS/tech/slave.txt for a full list of the
        available properties
        """

        args = args or []
        response = Response(output={})

        result = self._exec('set_property', property, value,
                            prefix='pausing_keep_force' if property != 'pause'
                            else None, wait_for_response=True, *args) or {}

        for k, v in result.items():
            if k == 'ERROR' and v not in response.errors:
                response.errors.append('{} {}{}: {}'.format(property, value,
                                                            args, v))
            else:
                response.output[k] = v

        return response

    @action
    def step_property(self, property, value, args=None):
        """
        Step a player property (e.g. volume, time_pos etc.). See
        https://www.mplayerhq.hu/DOCS/tech/slave.txt for a full list of the
        available steppable properties
        """

        args = args or []
        response = Response(output={})

        result = self._exec('step_property', property, value,
                            prefix='pausing_keep_force',
                            wait_for_response=True, *args) or {}

        for k, v in result.items():
            if k == 'ERROR' and v not in response.errors:
                response.errors.append('{} {}{}: {}'.format(property, value,
                                                            args, v))
            else:
                response.output[k] = v

        return response

    def set_subtitles(self, filename, *args, **kwargs):
        raise NotImplementedError


# vim:sw=4:ts=4:et:
