import json
import os
import re
import subprocess
import threading
import time
from dataclasses import asdict, dataclass
from multiprocessing import Process, Queue, RLock
from queue import Empty
from typing import Any, Collection, Dict, List, Optional

from platypush.message.response import Response
from platypush.plugins import action
from platypush.plugins.media import PlayerState, MediaPlugin
from platypush.message.event.media import (
    MediaPlayEvent,
    MediaPlayRequestEvent,
    MediaPauseEvent,
    MediaResumeEvent,
    MediaStopEvent,
    NewPlayingMediaEvent,
)
from platypush.utils import find_bins_in_path


@dataclass
class MplayerStatus:
    """
    MPlayer status object
    """

    state: PlayerState = PlayerState.STOP
    filename: Optional[str] = None
    path: Optional[str] = None
    title: Optional[str] = None
    duration: Optional[float] = None
    position: Optional[float] = None
    percent_pos: Optional[float] = None
    fullscreen: Optional[bool] = None
    mute: Optional[bool] = None
    pause: Optional[bool] = None
    volume: Optional[float] = None
    volume_max: Optional[float] = None
    seekable: Optional[bool] = None
    url: Optional[str] = None


class MediaMplayerPlugin(MediaPlugin):
    """
    Plugin to control MPlayer instances.

    Note that some plugin methods are populated dynamically by introspecting the
    mplayer executable. You can verify the supported methods at runtime by
    running the :meth:`.list_actions` action.
    """

    _mplayer_default_communicate_timeout = 0.5

    _mplayer_bin_default_args = [
        '-slave',
        '-quiet',
        '-idle',
        '-input',
        'nodefault-bindings',
        '-noconfig',
        'all',
    ]

    def __init__(
        self,
        fullscreen: bool = False,
        mplayer_bin: Optional[str] = None,
        mplayer_timeout: float = _mplayer_default_communicate_timeout,
        args: Optional[Collection[str]] = None,
        **kwargs,
    ):
        """
        :param fullscreen: If set to True then the player will be started in
            fullscreen mode (default: False)
        :param mplayer_bin: Path to the MPlayer executable (default: search for
            the first occurrence in your system PATH environment variable)
        :param mplayer_timeout: Timeout in seconds to wait for more data
            from MPlayer before considering a response ready (default: 0.5 seconds)
        :param args: Default arguments that will be passed to the MPlayer
            executable
        """

        super().__init__(**kwargs)

        self.args = args or []
        self._init_mplayer_bin(mplayer_bin=mplayer_bin)
        self._fullscreen = fullscreen
        self._build_actions()
        self._player = None
        self._mplayer_timeout = mplayer_timeout
        self._status_lock = threading.Lock()
        self._status = MplayerStatus()
        self._answer_queue = Queue()
        self._proc_monitor: Optional[Process] = None
        self._cmd_lock = RLock()
        self._cleanup_lock = RLock()

    def _init_mplayer_bin(self, mplayer_bin=None):
        if not mplayer_bin:
            bin_name = 'mplayer.exe' if os.name == 'nt' else 'mplayer'
            bins = find_bins_in_path(bin_name)

            if not bins:
                raise RuntimeError(
                    'MPlayer executable not specified and not '
                    + 'found in your PATH. Make sure that mplayer'
                    + 'is either installed or configured'
                )

            self.mplayer_bin = bins[0]
        else:
            mplayer_bin = os.path.expanduser(mplayer_bin)
            if not (
                os.path.isfile(mplayer_bin)
                and (os.name == 'nt' or os.access(mplayer_bin, os.X_OK))
            ):
                raise RuntimeError(
                    f'{mplayer_bin} is does not exist or is not a valid executable file'
                )

            self.mplayer_bin = mplayer_bin

    def _init_mplayer(self, mplayer_args=None):
        if self._player:
            try:
                self._player.terminate()
            except Exception as e:
                self.logger.debug('Failed to quit mplayer before _exec: %s', e)

        m_args = mplayer_args or []
        args = [self.mplayer_bin] + self._mplayer_bin_default_args
        if self._fullscreen and '-fs' not in args:
            args.append('-fs')

        for arg in (*self.args, *m_args):
            if arg not in args:
                args.append(arg)

        popen_args: Dict[str, Any] = {
            'stdin': subprocess.PIPE,
            'stdout': subprocess.PIPE,
        }

        if self._env:
            popen_args['env'] = self._env

        self._player = subprocess.Popen(args, **popen_args)
        self._proc_monitor = Process(target=self._listener, name='mplayer-monitor')
        self._proc_monitor.start()

    def _build_actions(self):
        """Populates the actions list by introspecting the mplayer executable"""

        def args_pprint(txt):
            lc = txt.lower()
            if lc[0] == '[':
                return f'{lc[1:-1]}=None'
            return lc

        self._actions = {}
        with subprocess.Popen(
            [self.mplayer_bin, '-input', 'cmdlist'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
        ) as mplayer:
            while True:
                if not mplayer.stdout:
                    break

                line = mplayer.stdout.readline()
                if not line:
                    break

                line = line.decode()
                if line[0].isupper():
                    continue

                args = line.split()
                cmd_name = args.pop(0)
                arguments = ', '.join([args_pprint(a) for a in args])
                self._actions[cmd_name] = f'{cmd_name}({arguments})'

    def _exec(
        self, cmd, *args, mplayer_args=None, prefix=None, wait_for_response=False
    ) -> Optional[dict]:
        cmd_name = cmd
        if cmd_name in {'loadfile', 'loadlist'}:
            self._init_mplayer(mplayer_args)
        else:
            if not self._player:
                self.logger.warning('MPlayer is not running')

        cmd = (
            f'{prefix + " " if prefix else ""}'
            + cmd_name
            + (" " if args else "")
            + " ".join(repr(a) for a in args)
            + '\n'
        ).encode()

        if not self._player:
            self.logger.debug('Cannot send command %s: player unavailable', cmd)
            return None

        if not (self._player.stdin and self._player.stdin.writable()):
            self.logger.warning(
                'Could not communicate with the mplayer process: the stdin is closed'
            )
            return None

        # Make sure that the response queue is empty before waiting for a new response
        while not self._answer_queue.empty():
            self._answer_queue.get()

        self.logger.debug('mplayer interface:: Sending command: %s', cmd)

        with self._cmd_lock:
            try:
                self._player.stdin.write(cmd)
                self._player.stdin.flush()
            except BrokenPipeError:
                self.logger.info('The MPlayer process has terminated')
                self._cleanup()
                return None
            except Exception as e:
                self.logger.warning(
                    'Failed to send command %s: %s: %s', cmd, type(e).__name__, e
                )
                return None

        if cmd_name in {'loadfile', 'loadlist'}:
            self._post_event(NewPlayingMediaEvent, resource=args[0])

        if not wait_for_response:
            return None

        # Get the response from the queue
        try:
            ret, status = self._answer_queue.get(
                block=True, timeout=self._mplayer_timeout
            )
            self._status = status
        except Empty:
            self.logger.warning('No response from mplayer for command %s', cmd)
            return None

        return ret

    def _process_answer(self, answer: dict):
        for k, v in answer.items():
            if k == 'pause':
                if v and self._status.state == PlayerState.PLAY:
                    self._status.state = PlayerState.PAUSE
                    self._post_event(MediaPauseEvent)
                elif not v:
                    if self._status.state == PlayerState.PAUSE:
                        self._post_event(MediaResumeEvent)
                    elif self._status.state == PlayerState.STOP:
                        self._post_event(MediaPlayEvent)

                    self._status.state = PlayerState.PLAY
            elif k == 'filename':
                self._status.filename = v
            elif k == 'path':
                self._status.path = v
                self._status.url = (
                    'file://' if os.path.isfile(v) else ''
                ) + self._status.path
            elif k == 'fullscreen':
                self._status.fullscreen = v
            elif k == 'mute':
                self._status.mute = v
            elif k == 'percent_pos':
                self._status.percent_pos = v
            elif k == 'time_pos':
                self._status.position = v
            elif k == 'volume':
                self._status.volume = v
            elif k == 'length':
                self._status.duration = v

        self._answer_queue.put((answer, self._status))

    def _status_checker(self):
        try:
            while self._player and self._player.stdin and self._player.stdin.writable():
                try:
                    self._get_property('filename')
                except (IOError, ValueError, KeyboardInterrupt):
                    break
                finally:
                    time.sleep(1)
        except Exception as e:
            self.logger.warning('mplayer status checker process failed: %s', e)

    def _listener(self):
        status_checker = Process(
            target=self._status_checker, name='mplayer-status-checker'
        )

        try:
            status_checker.start()

            while (
                self._player and self._player.stdout and self._player.stdout.readable()
            ):
                try:
                    buf = self._player.stdout.readline()
                except (IOError, ValueError, KeyboardInterrupt):
                    break

                line = buf.decode() if isinstance(buf, bytes) else buf
                self.logger.debug('mplayer interface:: Received line: %s', buf)

                if not line:
                    break

                if line.startswith('ANS_'):
                    m = re.match(r'^([^=]+)=(.*)\s*$', line[4:])
                    if not m:
                        self.logger.warning('Unexpected response: %s', line)
                        break

                    k, v = m.group(1), m.group(2)
                    if v == 'yes':
                        v = True
                    elif v == 'no':
                        v = False

                    try:
                        if isinstance(v, str):
                            v = json.loads(v)
                    except (TypeError, ValueError):
                        pass

                    self._process_answer({k: v})
                elif line.startswith('Starting playback'):
                    self._status.state = PlayerState.PLAY
                    self._post_event(MediaPlayEvent)
        finally:
            if status_checker and status_checker.is_alive():
                status_checker.terminate()
                status_checker.join(timeout=5)
                try:
                    status_checker.kill()
                except Exception:
                    pass

            if self._player:
                self._player.wait()
                try:
                    self.quit()
                except Exception:
                    pass

            self._player = None

    @action
    def execute(self, cmd, args=None):
        """
        Execute a raw MPlayer command. See
        https://www.mplayerhq.hu/DOCS/tech/slave.txt for a reference or call
        :meth:`.list_actions` to get a list
        """

        args = args or []
        return self._exec(cmd, *args)

    @action
    def list_actions(self):
        return [
            {'action': a, 'args': self._actions[a]}
            for a in sorted(self._actions.keys())
        ]

    def _post_event(self, evt_type, **evt):
        self._bus.post(
            evt_type(
                player='local',
                plugin='media.mplayer',
                resource=evt.pop('resource', self._status.url),
                title=self._status.title or self._status.filename,
                **evt,
            )
        )

    @action
    def play(
        self,
        resource: str,
        subtitles: Optional[str] = None,
        mplayer_args: Optional[List[str]] = None,
        **_,
    ):
        """
        Play a resource.

        :param resource: Resource to play - can be a local file or a remote URL
        :param subtitles: Path to optional subtitle file
        :param mplayer_args: Extra runtime arguments that will be passed to the
            MPlayer executable
        """

        self._post_event(MediaPlayRequestEvent, resource=resource)
        if subtitles:
            subs = self.get_subtitles_file(subtitles)
            if subs:
                mplayer_args = list(mplayer_args or []) + ['-sub', subs]

        resource = self._get_resource(resource)
        if resource.startswith('file://'):
            resource = resource[7:]

        self._exec('loadfile', resource, mplayer_args=mplayer_args)
        if self.volume:
            self.set_volume(volume=self.volume)

        return self.status()

    @action
    def pause(self, *_, **__):
        """Toggle the paused state"""
        self._exec('pause')
        return self.status()

    @action
    def stop(self, *_, **__):
        """Stop the playback"""
        return self.quit()

    def _cleanup(self):
        with self._cleanup_lock:
            if self._player:
                self._player.terminate()
                self._player.wait()
                try:
                    self._player.kill()
                except Exception:
                    pass

                self._player = None
                self._post_event(MediaStopEvent)

            if self._proc_monitor and os.getpid() != self._proc_monitor.pid:
                try:
                    self._proc_monitor.terminate()
                except Exception as e:
                    if self._proc_monitor or self._proc_monitor.is_alive():
                        self.logger.warning(
                            'Failed to terminate MPlayer monitor process: %s', e
                        )

                if self._proc_monitor:
                    try:
                        self._proc_monitor.join(timeout=5)
                    except AssertionError:  # Can only join a child process
                        pass

                try:
                    self._proc_monitor.kill()
                except Exception:
                    pass

                self._proc_monitor = None

    @action
    def quit(self, *_, **__):
        """Quit the player"""
        self._exec('quit')
        self._cleanup()
        return self.status()

    @action
    def voldown(self, *_, step=10.0, **__):
        """Volume down by (default: 10)%"""
        volume = (self._get_property('volume') or {}).get('volume')
        if volume is None:
            return self.status()

        return self.set_volume(volume=volume - step)

    @action
    def volup(self, *_, step=10.0, **__):
        """Volume up by (default: 10)%"""
        volume = (self._get_property('volume') or {}).get('volume')
        if volume is None:
            return self.status()

        return self.set_volume(volume=volume + step)

    @action
    def back(self, *_, offset=30.0, **__):
        """Back by (default: 30) seconds"""
        self.step_property('time_pos', -offset)
        return self.status()

    @action
    def forward(self, *_, offset=30.0, **__):
        """Forward by (default: 30) seconds"""
        self.step_property('time_pos', offset)
        return self.status()

    @action
    def toggle_subtitles(self, *_, **__):
        """Toggle the subtitles visibility"""
        response: dict = self._get_property('sub_visibility') or {}
        subs = response.get('sub_visibility')
        self._exec('sub_visibility', int(not subs))
        return self.status()

    @action
    def add_subtitles(self, filename: str, **__):
        """
        Sets media subtitles from filename

        :param filename: Subtitles file.
        """
        self._exec('sub_visibility', 1)
        self._exec('sub_load', filename)
        return self.status()

    @action
    def remove_subtitles(self, *_, index: Optional[int] = None, **__):
        """
        Removes the subtitle specified by the index (default: all)

        :param index: (1-based) index of the subtitles track to remove.
        """
        if index is None:
            self._exec('sub_remove', prefix='pausing_keep_force')
        else:
            self._exec('sub_remove', index, prefix='pausing_keep_force')

        return self.status()

    @action
    def is_playing(self, *_, **__):
        """
        :returns: True if it's playing, False otherwise
        """
        response: dict = self.get_property('pause').output or {}  # type: ignore
        return response.get('pause') is False

    @action
    def load(self, resource, *_, mplayer_args: Optional[Collection[str]] = None, **__):
        """
        Load a resource/video in the player.
        """
        if mplayer_args is None:
            mplayer_args = {}
        return self.play(resource, mplayer_args=mplayer_args)

    @action
    def mute(self, *_, **__):
        """Toggle mute state"""
        self._exec('mute', prefix='pausing_keep_force')
        return self.status()

    @action
    def seek(self, position: float, *_, **__):
        """
        Alias for :meth:`.set_position`

        :param position: Number of seconds relative to the current cursor
        """
        return self.set_position(position)

    @action
    def set_position(self, position: float, *_, **__):
        """
        Set the playback position.

        :param position: Number of seconds from the start
        """
        # cur_pos = (self._get_property('time_pos') or {}).get('time_pos')
        # if cur_pos is None:
        #     return self.status()

        # self.set_property('time_pos', position - cur_pos)
        self.set_property('time_pos', position)
        return self.status()

    @action
    def set_volume(self, volume: float, *_, **__):
        """
        Set the volume

        :param volume: Volume value between 0 and 100
        """
        self._exec('volume', max(0, min(100, volume)), 1, prefix='pausing_keep_force')
        return self.status()

    @action
    def status(self):
        """
        Get the current player state.

        :returns: A dictionary containing the current state.

        Example::

            .. code-block:: javascript

                {
                    "duration": 300.0,  // in seconds
                    "filename": "video.mp4",
                    "fullscreen": false,
                    "mute": false,
                    "name": "video.mp4",
                    "path": "/path/to/video.mp4",
                    "pause": false,
                    "percent_pos": 30.0,
                    "position": 90.0,  // in seconds
                    "seekable": true,
                    "state": "play",  // or "stop" or "pause"
                    "title": "My Video",
                    "volume": 50.0,
                    "volume_max": 100.0,
                    "url": "file:///path/to/video.mp4",
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
                if isinstance(value, dict):
                    status[prop] = value.get(player_prop)

        status['seekable'] = bool(status['duration'])
        status['state'] = (
            PlayerState.PAUSE.value if status['pause'] else PlayerState.PLAY.value
        )

        if status['path']:
            status['url'] = (
                'file://' if os.path.isfile(status['path']) else ''
            ) + status['path']

        status['volume_max'] = 100

        if self._latest_resource:
            status.update(
                {
                    k: v
                    for k, v in asdict(self._latest_resource).items()
                    if v is not None
                }
            )

        return status

    def _get_property(
        self,
        property: str,  # pylint: disable=redefined-builtin
        args: Optional[Collection[str]] = None,
    ) -> dict:
        args = args or []
        response = {}
        errors = []

        result = (
            self._exec(
                'get_property',
                property,
                prefix='pausing_keep_force',
                wait_for_response=True,
                *args,
            )
            or {}
        )

        if not result:
            return response

        for k, v in result.items():
            if k == 'ERROR' and v not in errors:
                self._handle_property_error(property, args, v, errors)
            else:
                response[k] = v

        assert not errors, f'get_property errors: {errors}'
        return response

    def _handle_property_error(
        self,
        property: str,  # pylint: disable=redefined-builtin
        args: Optional[Collection[str]],
        error: str,
        errors: List[str],
    ):
        if error == 'PROPERTY_UNAVAILABLE':
            # This is a workaround to detect the end-of-file event.
            # When get_property('filename') returns PROPERTY_UNAVAILABLE
            # it means that the player is no longer playing anything
            if property == 'filename' and self._status.state != PlayerState.STOP:
                self.quit()
        else:
            errors.append(f'{property}{args}: {error}')

    @action
    def get_property(
        self,
        property: str,  # pylint: disable=redefined-builtin
        args: Optional[Collection[str]] = None,
    ):
        """
        Get a player property (e.g. pause, fullscreen etc.). See
        https://www.mplayerhq.hu/DOCS/tech/slave.txt for a full list of the
        available properties
        """
        return self._get_property(property, args=args)

    @action
    def set_property(
        self,
        property: str,  # pylint: disable=redefined-builtin
        value: Any,
        args: Optional[Collection[str]] = None,
    ):
        """
        Set a player property (e.g. pause, fullscreen etc.). See
        https://www.mplayerhq.hu/DOCS/tech/slave.txt for a full list of the
        available properties
        """

        args = args or []
        response = Response(output={})

        result = (
            self._exec(
                'set_property',
                property,
                value,
                prefix='pausing_keep_force' if property != 'pause' else None,
                wait_for_response=True,
                *args,
            )
            or {}
        )

        for k, v in result.items():
            if k == 'ERROR' and v not in response.errors:
                if not isinstance(response.errors, list):
                    response.errors = []
                response.errors.append(f'{property} {value}{args}: {v}')
            else:
                if not isinstance(response.output, dict):
                    response.output = {}
                response.output[k] = v

        return response

    @action
    def step_property(
        self,
        property: str,  # pylint: disable=redefined-builtin
        value: Any,
        *_,
        args: Optional[Collection[str]] = None,
        **__,
    ):
        """
        Step a player property (e.g. volume, time_pos etc.). See
        https://www.mplayerhq.hu/DOCS/tech/slave.txt for a full list of the
        available steppable properties
        """

        args = args or []
        response = Response(output={})

        result = (
            self._exec(
                'step_property',
                property,
                value,
                prefix='pausing_keep_force',
                wait_for_response=True,
                *args,
            )
            or {}
        )

        for k, v in result.items():
            if k == 'ERROR' and v not in response.errors:
                if not isinstance(response.errors, list):
                    response.errors = []
                response.errors.append(f'{property} {value}{args}: {v}')
            else:
                if not isinstance(response.output, dict):
                    response.output = {}
                response.output[k] = v

        return response

    def set_subtitles(self, filename: str, *_, **__):
        self.logger.debug('set_subtitles called with filename=%s', filename)
        raise NotImplementedError


# vim:sw=4:ts=4:et:
