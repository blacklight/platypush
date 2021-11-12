import json
import os
import subprocess
import threading
from typing import Optional, Dict, Any

from platypush.backend import Backend
from platypush.common.spotify import SpotifyMixin
from platypush.config import Config
from platypush.message.event.music import MusicPlayEvent, MusicPauseEvent, MusicStopEvent, \
    NewPlayingTrackEvent, SeekChangeEvent, VolumeChangeEvent
from platypush.utils import get_redis

from .event import status_queue


class MusicSpotifyBackend(Backend, SpotifyMixin):
    """
    This backend uses `librespot <https://github.com/librespot-org/librespot>`_ to turn Platypush into an audio client
    compatible with Spotify Connect and discoverable by a device running a Spotify client or app. It can be used to
    stream Spotify through the Platypush host. After the backend has started, you should see a new entry in the
    Spotify Connect devices list in your app.

    Triggers:

        * :class:`platypush.message.event.music.MusicPlayEvent` if the playback state changed to play
        * :class:`platypush.message.event.music.MusicPauseEvent` if the playback state changed to pause
        * :class:`platypush.message.event.music.MusicStopEvent` if the playback state changed to stop
        * :class:`platypush.message.event.music.NewPlayingTrackEvent` if a new track is being played
        * :class:`platypush.message.event.music.VolumeChangeEvent` if the volume changes

    Requires:

        * **librespot**. Consult the `README <https://github.com/librespot-org/librespot>`_ for instructions.

    """

    def __init__(self,
                 librespot_path: str = 'librespot',
                 device_name: Optional[str] = None,
                 device_type: str = 'speaker',
                 audio_backend: str = 'alsa',
                 audio_device: Optional[str] = None,
                 mixer: str = 'softvol',
                 mixer_name: str = 'PCM',
                 mixer_card: str = 'default',
                 mixer_index: int = 0,
                 volume: int = 100,
                 volume_ctrl: str = 'linear',
                 bitrate: int = 160,
                 autoplay: bool = False,
                 disable_gapless: bool = False,
                 username: Optional[str] = None,
                 password: Optional[str] = None,
                 client_id: Optional[str] = None,
                 client_secret: Optional[str] = None,
                 proxy: Optional[str] = None,
                 ap_port: Optional[int] = None,
                 disable_discovery: bool = False,
                 cache_dir: Optional[str] = None,
                 system_cache_dir: Optional[str] = None,
                 disable_audio_cache=False,
                 enable_volume_normalization: bool = False,
                 normalization_method: str = 'dynamic',
                 normalization_pre_gain: Optional[float] = None,
                 normalization_threshold: float = -1.,
                 normalization_attack: int = 5,
                 normalization_release: int = 100,
                 normalization_knee: float = 1.,
                 **kwargs):
        """
        :param librespot_path: Librespot path/executable name (default: ``librespot``).
        :param device_name: Device name (default: same as configured Platypush ``device_id`` or hostname).
        :param device_type: Device type to be shown in the icon. Available types:
            ``unknown``, ``computer``, ``tablet``, ``smartphone``, ``speaker``, ``tv``,
            ``avr`` (Audio/Video Receiver), ``stb`` (Set-Top Box), or ``audiodongle`` (default: ``speaker``).
        :param audio_backend: Audio backend to be used. Supported values:
            ``alsa``, ``portaudio``, ``pulseaudio``, ``jackaudio``, ``gstreamer``, ``rodio``, ``rodiojack``,
            ``sdl`` (default: ``alsa``).
        :param audio_device: Output audio device. Type ``librespot --device ?`` to get a list of the available devices.
        :param mixer: Mixer to be used to control the volume. Supported values: ``alsa`` or ``softvol``
            (default: ``softvol``).
        :param mixer_name: Mixer name if using the ALSA mixer. Supported values: ``PCM`` or ``Master``
            (default: ``PCM``).
        :param mixer_card: ALSA mixer output card, as reported by ``aplay -l`` (default: ``default``).
        :param mixer_index: ALSA card index, as reported by ``aplay -l`` (default: 0).
        :param volume: Initial volume, as an integer between 0 and 100 if ``volume_ctrl=linear`` or in dB if
            ``volume_ctrl=logarithmic``.
        :param volume_ctrl: Volume control scale. Supported values: ``linear`` and ``logarithmic``
            (default: ``linear``).
        :param bitrate: Audio bitrate. Choose 320 for maximum quality (default: 160).
        :param autoplay: Play similar tracks when the queue ends (default: False).
        :param disable_gapless: Disable gapless audio (default: False).
        :param username: Spotify user/device username (used if you want to enable Spotify Connect remotely).
        :param password: Spotify user/device password (used if you want to enable Spotify Connect remotely).
        :param client_id: Spotify client ID, required if you want to retrieve track and album info through the
            Spotify Web API. You can generate one by creating a Spotify app `here <https://developer.spotify.com/>`.
        :param client_secret: Spotify client secret, required if you want to retrieve track and album info
            through the Spotify Web API. You can generate one by creating a Spotify app
            `here <https://developer.spotify.com/>`.
        :param proxy: Optional HTTP proxy configuration.
        :param ap_port: Spotify AP port to be used (default: default ports, i.e. 80, 443 and 4070).
        :param disable_discovery: Disable discovery mode.
        :param cache_dir: Data files cache directory.
        :param system_cache_dir: System cache directory - it includes audio settings and credentials.
        :param disable_audio_cache: Disable audio caching (default: False).
        :param enable_volume_normalization: Play all the tracks at about the same volume (default: False).
        :param normalization_method: If ``enable_volume_normalization=True``, this setting specifies the volume
            normalization method. Supported values: ``basic``, ``dynamic`` (default: ``dynamic``).
        :param normalization_pre_gain: Pre-gain applied to volume normalization if ``enable_volume_normalization=True``,
            expressed in dB.
        :param normalization_threshold: If ``enable_volume_normalization=True``, this setting specifies the
            normalization threshold (in dBFS) to prevent audio clipping (default: -1.0).
        :param normalization_attack: If ``enable_volume_normalization=True``, this setting specifies the attack time
            (in ms) during which the dynamic limiter is reducing the gain (default: 5).
        :param normalization_release: If ``enable_volume_normalization=True``, this setting specifies the release time
            (in ms) for the dynamic limiter to restore the gain (default: 100).
        :param normalization_knee: Knee steepness of the dynamic limiter (default: 1.0).
        """
        Backend.__init__(self, **kwargs)
        SpotifyMixin.__init__(self, client_id=client_id, client_secret=client_secret)
        self.device_name = device_name or Config.get('device_id')
        self._librespot_args = [
            librespot_path, '--name', self.device_name, '--backend', audio_backend,
            '--device-type', device_type, '--mixer', mixer, '--alsa-mixer-control', mixer_name,
            '--initial-volume', str(volume), '--volume-ctrl', volume_ctrl, '--bitrate', str(bitrate),
            '--emit-sink-events', '--onevent', 'python -m platypush.backend.music.spotify.event',
        ]

        if audio_device:
            self._librespot_args += ['--alsa-mixer-device', audio_device]
        else:
            self._librespot_args += [
                '--alsa-mixer-device', mixer_card, '--alsa-mixer-index', str(mixer_index)
            ]
        if autoplay:
            self._librespot_args += ['--autoplay']
        if disable_gapless:
            self._librespot_args += ['--disable-gapless']
        if disable_discovery:
            self._librespot_args += ['--disable-discovery']
        if disable_audio_cache:
            self._librespot_args += ['--disable-audio-cache']
        if proxy:
            self._librespot_args += ['--proxy', proxy]
        if ap_port:
            self._librespot_args += ['--ap-port', str(ap_port)]
        if cache_dir:
            self._librespot_args += ['--cache', os.path.expanduser(cache_dir)]
        if system_cache_dir:
            self._librespot_args += ['--system-cache', os.path.expanduser(system_cache_dir)]
        if enable_volume_normalization:
            self._librespot_args += [
                '--enable-volume-normalisation', '--normalisation-method', normalization_method,
                '--normalisation-threshold', str(normalization_threshold), '--normalisation-attack',
                str(normalization_attack), '--normalisation-release', str(normalization_release),
                '--normalisation-knee', str(normalization_knee),
            ]

            if normalization_pre_gain:
                self._librespot_args += ['--normalisation-pregain', str(normalization_pre_gain)]

        self._librespot_dump_args = self._librespot_args.copy()
        if username and password:
            self._librespot_args += ['--username', username, '--password', password]
            self._librespot_dump_args += ['--username', username, '--password', '*****']

        self._librespot_proc: Optional[subprocess.Popen] = None
        self._status_thread: Optional[threading.Thread] = None

        self.status: Dict[str, Any] = {
            'state': 'stop',
            'volume': None,
            'time': None,
            'elapsed': None,
        }

        self.track = {
            'file': None,
            'url': None,
            'uri': None,
            'time': None,
            'artist': None,
            'album': None,
            'title': None,
            'date': None,
            'track': None,
            'id': None,
            'x-albumuri': None,
        }

    def run(self):
        super().run()
        self._status_thread = threading.Thread(target=self._get_status_check_loop())
        self._status_thread.start()

        while not self.should_stop():
            self.logger.info(
                f'Starting music.spotify backend. Librespot command line: {self._librespot_dump_args}'
            )

            try:
                self._librespot_proc = subprocess.Popen(self._librespot_args)

                while not self.should_stop():
                    try:
                        if self._librespot_proc:
                            self._librespot_proc.wait(timeout=1.0)
                    except subprocess.TimeoutExpired:
                        pass
            except Exception as e:
                self.logger.exception(e)
                continue

    def _get_status_check_loop(self):
        def loop():
            redis = get_redis()

            while not self.should_stop():
                msg = redis.blpop(status_queue, timeout=1)
                if not msg:
                    continue

                self._process_status_msg(json.loads(msg[1]))

        return loop

    def _process_status_msg(self, status):
        event_type = status.get('PLAYER_EVENT')
        volume = int(status['VOLUME'])/655.35 if status.get('VOLUME') is not None else None
        track_id = status.get('TRACK_ID')
        old_track_id = status.get('OLD_TRACK_ID', self.track['id'])
        duration = int(status['DURATION_MS'])/1000. if status.get('DURATION_MS') is not None else None
        elapsed = int(status['POSITION_MS'])/1000. if status.get('POSITION_MS') is not None else None

        if volume is not None:
            self.status['volume'] = volume
        if duration is not None:
            self.status['time'] = duration
        if elapsed is not None:
            self.status['elapsed'] = elapsed
        if track_id and track_id != old_track_id:
            self.track = self.spotify_get_track(track_id)

        if event_type == 'playing':
            self.status['state'] = 'play'
        elif event_type == 'paused':
            self.status['state'] = 'pause'
        elif event_type in ['stopped', 'started']:
            self.status['state'] = 'stop'

        event_args = {
            'status': self.status,
            'track': self.track,
            'plugin_name': 'music.spotify',
            'player': self.device_name,
        }

        if event_type == 'volume_set':
            self.bus.post(VolumeChangeEvent(volume=volume, **event_args))
        if elapsed is not None:
            self.bus.post(SeekChangeEvent(position=elapsed, **event_args))
        if track_id and track_id != old_track_id:
            self.bus.post(NewPlayingTrackEvent(**event_args))
        if event_type == 'playing':
            self.bus.post(MusicPlayEvent(**event_args))
        elif event_type == 'paused':
            self.bus.post(MusicPauseEvent(**event_args))
        elif event_type == 'stopped':
            self.bus.post(MusicStopEvent(**event_args))

    def on_stop(self):
        if self._librespot_proc:
            self.logger.info('Terminating librespot')
            self._librespot_proc.terminate()

            try:
                self._librespot_proc.wait(timeout=5.)
            except subprocess.TimeoutExpired:
                self.logger.warning('Librespot has not yet terminated: killing it')
                self._librespot_proc.kill()

            self._librespot_proc = None

        if self._status_thread.is_alive():
            self.logger.info('Waiting for the status check thread to terminate')
            self._status_thread.join(timeout=10)
