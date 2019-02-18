import os
import tempfile
import threading
import time

from platypush.context import get_bus, get_plugin
from platypush.message.response import Response
from platypush.plugins.media import PlayerState, MediaPlugin
from platypush.message.event.media import MediaPlayEvent, MediaPlayRequestEvent, \
    MediaPauseEvent, MediaStopEvent, NewPlayingMediaEvent

from platypush.plugins import action


# XXX WORK IN PROGRESS
class MediaMpvPlugin(MediaPlugin):
    """
    Plugin to control MPV instances

    Requires:

        * **python-mpv** (``pip install python-mpv``)
        * **mpv** executable on your system
    """

    _mpv_default_communicate_timeout = 0.5

    _mpv_properties = [
        'osdlevel', 'speed', 'loop', 'pause', 'filename', 'path', 'demuxer',
        'stream_pos', 'stream_start', 'stream_end', 'stream_length',
        'stream_time_pos', 'titles', 'chapter', 'chapters', 'angle', 'length',
        'percent_pos', 'time_pos', 'metadata', 'metadata', 'volume', 'balance',
        'mute', 'audio_delay', 'audio_format', 'audio_codec', 'audio_bitrate',
        'samplerate', 'channels', 'switch_audio', 'switch_angle',
        'switch_title', 'capturing', 'fullscreen', 'deinterlace', 'ontop',
        'rootwin', 'border', 'framedropping', 'gamma', 'brightness', 'contrast',
        'saturation', 'hue', 'panscan', 'vsync', 'video_format', 'video_codec',
        'video_bitrate', 'width', 'height', 'fps', 'aspect', 'switch_video',
        'switch_program', 'sub', 'sub_source', 'sub_file', 'sub_vob',
        'sub_demux', 'sub_delay', 'sub_pos', 'sub_alignment', 'sub_visibility',
        'sub_forced_only', 'sub_scale', 'tv_brightness', 'tv_contrast',
        'tv_saturation', 'tv_hue', 'teletext_page', 'teletext_subpage',
        'teletext_mode', 'teletext_format',
    ]

    def __init__(self, mpv_bin=None,
                 mpv_timeout=_mpv_default_communicate_timeout,
                 args=None, *argv, **kwargs):
        """
        Create the MPV wrapper.

        :param mpv_bin: Path to the mpv executable (default: search for
            the first occurrence in your system PATH environment variable)
        :type mpv_bin: str

        :param mpv_timeout: Timeout in seconds to wait for more data
            from MPV before considering a response ready (default: 0.5 seconds)
        :type mpv_timeout: float

        :param args: Default arguments that will be passed to the mpv executable
        :type args: list
        """

        super().__init__(*argv, **kwargs)

        self.args = args or []
        self._init_mpv_bin()
        self._build_actions()
        self._player = None
        self._mpv_timeout = mpv_timeout
        self._mpv_stopped_event = threading.Event()
        self._is_playing_torrent = False


    def _init_mpv_bin(self, mpv_bin=None):
        if not mpv_bin:
            bin_name = 'mpv.exe' if os.name == 'nt' else 'mpv'
            bins = find_bins_in_path(bin_name)

            if not bins:
                raise RuntimeError('mpv executable not specified and not ' +
                                   'found in your PATH. Make sure that mpv' +
                                   'is either installed or configured')

            self.mpv_bin = bins[0]
        else:
            mpv_bin = os.path.expanduser(mpv_bin)
            if not (os.path.isfile(mpv_bin)
                    and (os.name == 'nt' or os.access(mpv_bin, os.X_OK))):
                raise RuntimeError('{} is does not exist or is not a valid ' +
                                   'executable file'.format(mpv_bin))

            self.mpv_bin = mpv_bin

    def _init_mpv(self, mpv_args=None):
        if self._player:
            try:
                self._player.quit()
            except:
                self.logger.debug('Failed to quit mpv before _exec: {}'.
                                  format(str))

        mpv_args = mpv_args or []
        args = [self.mpv_bin] + self._mpv_bin_default_args
        for arg in self.args + mpv_args:
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

    def _exec(self, cmd, *args, mpv_args=None, prefix=None,
              wait_for_response=False):
        cmd_name = cmd
        response = None

        if cmd_name == 'loadfile' or cmd_name == 'loadlist':
            self._init_mpv(mpv_args)
        else:
            if not self._player:
                self.logger.warning('mpv is not running')

        cmd = '{}{}{}{}\n'.format(
            prefix + ' ' if prefix else '',
            cmd_name, ' ' if args else '',
            ' '.join(repr(a) for a in args)).encode()

        self._player.stdin.write(cmd)
        self._player.stdin.flush()
        bus = get_bus()

        if cmd_name == 'loadfile' or cmd_name == 'loadlist':
            bus.post(NewPlayingMediaEvent(resource=args[0]))
        elif cmd_name == 'pause':
            bus.post(MediaPauseEvent())
        elif cmd_name == 'quit' or cmd_name == 'stop':
            if cmd_name == 'quit':
                self._player.terminate()
                self._player.wait()
                try: self._player.kill()
                except: pass
                self._player = None

        if not wait_for_response:
            return

        poll = select.poll()
        poll.register(self._player.stdout, select.POLLIN)
        last_read_time = time.time()

        while time.time() - last_read_time < self._mpv_timeout:
            result = poll.poll(0)
            if result:
                line = self._player.stdout.readline().decode()
                last_read_time = time.time()

                if line.startswith('ANS_'):
                    k, v = tuple(line[4:].split('='))
                    v = v.strip()
                    if v == 'yes': v = True
                    elif v == 'no': v = False

                    try: v = eval(v)
                    except: pass
                    response = { k: v }

        return response

    @action
    def execute(self, cmd, args=None):
        """
        Execute a raw mpv command.
        """

        args = args or []
        return self._exec(cmd, *args)

    @action
    def list_actions(self):
        return [ { 'action': action, 'args': self._actions[action] }
                for action in sorted(self._actions.keys()) ]

    def _process_monitor(self):
        def _thread():
            if not self._player:
                return

            self._mpv_stopped_event.clear()
            self._player.wait()
            try: self.quit()
            except: pass

            get_bus().post(MediaStopEvent())
            self._mpv_stopped_event.set()
            self._player = None

        return _thread

    def _get_subtitles_file(self, subtitles):
        if not subtitles:
            return

        if subtitles.startswith('file://'):
            subtitles = subtitles[len('file://'):]
        if os.path.isfile(subtitles):
            return os.path.abspath(subtitles)
        else:
            import requests
            content = requests.get(subtitles).content
            f = tempfile.NamedTemporaryFile(prefix='media_subs_',
                                            suffix='.srt', delete=False)

            with f:
                f.write(content)
            return f.name


    @action
    def play(self, resource, subtitles=None, mpv_args=None):
        """
        Play a resource.

        :param resource: Resource to play - can be a local file or a remote URL
        :type resource: str

        :param subtitles: Path to optional subtitle file
        :type subtitles: str

        :param mpv_args: Extra runtime arguments that will be passed to the
            mpv executable
        :type mpv_args: list[str]
        """

        get_bus().post(MediaPlayRequestEvent(resource=resource))
        if subtitles:
            mpv_args = mpv_args or []
            mpv_args += ['-sub', self._get_subtitles_file(subtitles)]

        resource = self._get_resource(resource)
        if resource.startswith('file://'):
            resource = resource[7:]
        elif resource.startswith('magnet:?'):
            self._is_playing_torrent = True
            return get_plugin('media.webtorrent').play(resource)

        self._is_playing_torrent = False
        ret = self._exec('loadfile', resource, mpv_args=mpv_args)
        get_bus().post(MediaPlayEvent(resource=resource))
        return ret

    @action
    def pause(self):
        """ Toggle the paused state """
        ret = self._exec('pause')
        get_bus().post(MediaPauseEvent())
        return ret

    def _stop_torrent(self):
        if self._is_playing_torrent:
            try:
                get_plugin('media.webtorrent').quit()
            except:
                self.logger.warning('Cannot quit the webtorrent instance: {}'.
                                    format(str(e)))

    @action
    def stop(self):
        """ Stop the playback """
        # return self._exec('stop')
        return self.quit()

    @action
    def quit(self):
        """ Quit the player """
        self._stop_torrent()
        self._exec('quit')
        get_bus().post(MediaStopEvent())

    @action
    def voldown(self, step=10.0):
        """ Volume down by (default: 10)% """
        return self._exec('volume', -step*10)

    @action
    def volup(self, step=10.0):
        """ Volume up by (default: 10)% """
        return self._exec('volume', step*10)

    @action
    def back(self, offset=60.0):
        """ Back by (default: 60) seconds """
        return self.step_property('time_pos', -offset)

    @action
    def forward(self, offset=60.0):
        """ Forward by (default: 60) seconds """
        return self.step_property('time_pos', offset)

    @action
    def toggle_subtitles(self):
        """ Toggle the subtitles visibility """
        subs = self.get_property('sub_visibility').output.get('sub_visibility')
        return self._exec('sub_visibility', int(not subs))

    @action
    def set_subtitles(self, filename):
        """ Sets media subtitles from filename """
        self._exec('sub_visibility', 1)
        return self._exec('sub_load', filename)

    @action
    def remove_subtitles(self, index=None):
        """ Removes the subtitle specified by the index (default: all) """
        if index is None:
            return self._exec('sub_remove')
        else:
            return self._exec('sub_remove', index)

    @action
    def is_playing(self):
        """
        :returns: True if it's playing, False otherwise
        """
        return self.get_property('pause').output.get('pause') == False

    @action
    def load(self, resource, mpv_args={}):
        """
        Load a resource/video in the player.
        """
        return self.play(resource, mpv_args=mpv_args)

    @action
    def mute(self):
        """ Toggle mute state """
        return self._exec('mute')

    @action
    def seek(self, position):
        """
        Seek backward/forward by the specified number of seconds

        :param relative_position: Number of seconds relative to the current cursor
        :type relative_position: int
        """
        return self.step_property('time_pos', position)

    @action
    def set_position(self, position):
        """
        Seek backward/forward to the specified absolute position

        :param position: Number of seconds from the start
        :type position: int
        """
        return self.set_property('time_pos', position)

    @action
    def set_volume(self, volume):
        """
        Set the volume

        :param volume: Volume value between 0 and 100
        :type volume: float
        """
        return self._exec('volume', volume)

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

        state = { 'state': PlayerState.STOP.value }

        try:
            paused = self.get_property('pause').output.get('pause')
            if paused is True:
                state['state'] = PlayerState.PAUSE.value
            elif paused is False:
                state['state'] = PlayerState.PLAY.value
        except:
            pass
        finally:
            return state

    @action
    def get_property(self, property, args=None):
        """
        Get a player property (e.g. pause, fullscreen etc.). See
        http://www.mpvhq.hu/DOCS/tech/slave.txt for a full list of the
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
        Set a player property (e.g. pause, fullscreen etc.).
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
        Step a player property (e.g. volume, time_pos etc.).
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


# vim:sw=4:ts=4:et:
