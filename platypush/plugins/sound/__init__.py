from collections import defaultdict
import os
import queue
import stat
from typing_extensions import override
import warnings

from threading import Event, RLock
from typing import Dict, Optional, Union

import sounddevice as sd
import soundfile as sf

from platypush.plugins import RunnablePlugin, action

from .core import Sound, Mix
from ._controllers import AudioRecorder
from ._model import AudioState


class SoundPlugin(RunnablePlugin):
    """
    Plugin to interact with a sound device.

    Triggers:

        * :class:`platypush.message.event.sound.SoundPlaybackStartedEvent` on playback start
        * :class:`platypush.message.event.sound.SoundPlaybackStoppedEvent` on playback stop
        * :class:`platypush.message.event.sound.SoundPlaybackPausedEvent` on playback pause
        * :class:`platypush.message.event.sound.SoundRecordingStartedEvent` on recording start
        * :class:`platypush.message.event.sound.SoundRecordingStoppedEvent` on recording stop
        * :class:`platypush.message.event.sound.SoundRecordingPausedEvent` on recording pause

    Requires:

        * **sounddevice** (``pip install sounddevice``)
        * **soundfile** (``pip install soundfile``)
        * **numpy** (``pip install numpy``)
        * **ffmpeg** package installed on the system (for streaming support)

    """

    _STREAM_NAME_PREFIX = 'platypush-stream-'

    def __init__(
        self,
        input_device=None,
        output_device=None,
        input_blocksize=Sound._DEFAULT_BLOCKSIZE,
        output_blocksize=Sound._DEFAULT_BLOCKSIZE,
        ffmpeg_bin: str = 'ffmpeg',
        **kwargs,
    ):
        """
        :param input_device: Index or name of the default input device. Use
            :meth:`platypush.plugins.sound.query_devices` to get the
            available devices. Default: system default
        :type input_device: int or str

        :param output_device: Index or name of the default output device.
            Use :meth:`platypush.plugins.sound.query_devices` to get the
            available devices. Default: system default
        :type output_device: int or str

        :param input_blocksize: Blocksize to be applied to the input device.
            Try to increase this value if you get input overflow errors while
            recording. Default: 1024
        :type input_blocksize: int

        :param output_blocksize: Blocksize to be applied to the output device.
            Try to increase this value if you get output underflow errors while
            playing. Default: 1024
        :type output_blocksize: int

        :param ffmpeg_bin: Path of the ``ffmpeg`` binary (default: search for
            the ``ffmpeg`` in the ``PATH``).
        """

        super().__init__(**kwargs)

        self.input_device = input_device
        self.output_device = output_device
        self.input_blocksize = input_blocksize
        self.output_blocksize = output_blocksize

        self.playback_state = {}
        self.playback_state_lock = RLock()
        self.playback_paused_changed = {}
        self.stream_mixes = {}
        self.active_streams = {}
        self.stream_name_to_index = {}
        self.stream_index_to_name = {}
        self.completed_callback_events = {}
        self.ffmpeg_bin = ffmpeg_bin

        self._recorders: Dict[str, AudioRecorder] = {}
        self._recorder_locks: Dict[str, RLock] = defaultdict(RLock)

    @staticmethod
    def _get_default_device(category: str) -> str:
        """
        Query the default audio devices.

        :param category: Device category to query. Can be either input or output
        """
        host_apis = sd.query_hostapis()
        assert host_apis, 'No sound devices found'
        available_devices = list(
            filter(
                lambda x: x is not None,
                (
                    host_api.get('default_' + category.lower() + '_device')  # type: ignore
                    for host_api in host_apis
                ),
            ),
        )

        assert available_devices, f'No default "{category}" device found'
        return available_devices[0]

    @action
    def query_devices(self, category=None):
        """
        Query the available devices

        :param category: Device category to query. Can be either input or output. Default: None (query all devices)
        :type category: str

        :returns: A dictionary representing the available devices.

        Example::

            [
                {
                    "name": "pulse",
                    "hostapi": 0,
                    "max_input_channels": 32,
                    "max_output_channels": 32,
                    "default_low_input_latency": 0.008684807256235827,
                    "default_low_output_latency": 0.008684807256235827,
                    "default_high_input_latency": 0.034807256235827665,
                    "default_high_output_latency": 0.034807256235827665,
                    "default_samplerate": 44100
                },
                {
                    "name": "default",
                    "hostapi": 0,
                    "max_input_channels": 32,
                    "max_output_channels": 32,
                    "default_low_input_latency": 0.008684807256235827,
                    "default_low_output_latency": 0.008684807256235827,
                    "default_high_input_latency": 0.034807256235827665,
                    "default_high_output_latency": 0.034807256235827665,
                    "default_samplerate": 44100
                }
            ]

        """

        devs = sd.query_devices()
        if category == 'input':
            devs = [d for d in devs if d.get('max_input_channels') > 0]  # type: ignore
        elif category == 'output':
            devs = [d for d in devs if d.get('max_output_channels') > 0]  # type: ignore

        return devs

    def _play_audio_callback(self, q, blocksize, streamtype, stream_index):
        is_raw_stream = streamtype == sd.RawOutputStream

        def audio_callback(outdata, frames, *, status):
            if self._get_playback_state(stream_index) == AudioState.STOPPED:
                raise sd.CallbackStop

            while self._get_playback_state(stream_index) == AudioState.PAUSED:
                self.playback_paused_changed[stream_index].wait()

            if frames != blocksize:
                self.logger.warning(
                    'Received %d frames, expected blocksize is %d', frames, blocksize
                )
                return

            if status.output_underflow:
                self.logger.warning('Output underflow: increase blocksize?')
                outdata[:] = (b'\x00' if is_raw_stream else 0.0) * len(outdata)
                return

            if status:
                self.logger.warning('Audio callback failed: %s', status)

            try:
                data = q.get_nowait()
            except queue.Empty:
                self.logger.warning('Buffer is empty: increase buffersize?')
                raise sd.CallbackStop

            if len(data) < len(outdata):
                outdata[: len(data)] = data
                outdata[len(data) :] = (b'\x00' if is_raw_stream else 0.0) * (
                    len(outdata) - len(data)
                )
            else:
                outdata[:] = data

        return audio_callback

    @action
    def play(
        self,
        file=None,
        sound=None,
        device=None,
        blocksize=None,
        bufsize=None,
        samplerate=None,
        channels=None,
        stream_name=None,
        stream_index=None,
    ):
        """
        Plays a sound file (support formats: wav, raw) or a synthetic sound.

        :param file: Sound file path. Specify this if you want to play a file
        :type file: str

        :param sound: Sound to play. Specify this if you want to play
            synthetic sounds. You can also create polyphonic sounds by just
            calling play multiple times.
        :type sound: Sound. You can initialize it either from a list
            of `Sound` objects or from its JSON representation, e.g.::

                {
                    "midi_note": 69,  # 440 Hz A
                    "gain":      1.0, # Maximum volume
                    "duration":  1.0  # 1 second or until release/pause/stop
                }

        :param device: Output device (default: default configured device or
            system default audio output if not configured)
        :type device: int or str

        :param blocksize: Audio block size (default: configured
            `output_blocksize` or 2048)
        :type blocksize: int

        :param bufsize: Size of the audio buffer (default: 20 frames for audio
            files, 2 frames for synth sounds)
        :type bufsize: int

        :param samplerate: Audio samplerate. Default: audio file samplerate if
            in file mode, 44100 Hz if in synth mode
        :type samplerate: int

        :param channels: Number of audio channels. Default: number of channels
            in the audio file in file mode, 1 if in synth mode
        :type channels: int

        :param stream_index: If specified, play to an already active stream
            index (you can get them through
            :meth:`platypush.plugins.sound.query_streams`). Default:
            creates a new audio stream through PortAudio.
        :type stream_index: int

        :param stream_name: Name of the stream to play to. If set, the sound
            will be played to the specified stream name, or a stream with that
            name will be created. If not set, and ``stream_index`` is not set
            either, then a new stream will be created on the next available
            index and named ``platypush-stream-<index>``.
        :type stream_name: str
        """

        if not file and not sound:
            raise RuntimeError(
                'Please specify either a file to play or a ' + 'list of sound objects'
            )

        if blocksize is None:
            blocksize = self.output_blocksize

        if bufsize is None:
            if file:
                bufsize = Sound._DEFAULT_FILE_BUFSIZE
            else:
                bufsize = Sound._DEFAULT_SYNTH_BUFSIZE

        q = queue.Queue(maxsize=bufsize)
        f = None
        t = 0.0

        if file:
            file = os.path.abspath(os.path.expanduser(file))

        if device is None:
            device = self.output_device
        if device is None:
            device = self._get_default_device('output')

        if file:
            f = sf.SoundFile(file)
        if not samplerate:
            samplerate = f.samplerate if f else Sound._DEFAULT_SAMPLERATE
        if not channels:
            channels = f.channels if f else 1

        mix = None
        with self.playback_state_lock:
            stream_index, is_new_stream = self._get_or_allocate_stream_index(
                stream_index=stream_index, stream_name=stream_name
            )

            if sound and stream_index in self.stream_mixes:
                mix = self.stream_mixes[stream_index]
                mix.add(sound)

        if not mix:
            return None, "Unable to allocate the stream"

        self.logger.info(
            'Starting playback of %s to sound device [%s] on stream [%s]',
            file or sound,
            device,
            stream_index,
        )

        if not is_new_stream:
            return  # Let the existing callback handle the new mix
            # TODO Potential support also for mixed streams with
            # multiple sound files and synth sounds?

        try:
            # Audio queue pre-fill loop
            for _ in range(bufsize):
                if f:
                    data = f.buffer_read(blocksize, dtype='float32')
                    if not data:
                        break
                else:
                    duration = mix.duration()
                    blocktime = float(blocksize / samplerate)
                    next_t = (
                        min(t + blocktime, duration)
                        if duration is not None
                        else t + blocktime
                    )

                    data = mix.get_wave(t_start=t, t_end=next_t, samplerate=samplerate)
                    t = next_t

                    if duration is not None and t >= duration:
                        break

                q.put_nowait(data)  # Pre-fill the audio queue

            stream = self.active_streams[stream_index]
            completed_callback_event = self.completed_callback_events[stream_index]

            if stream is None:
                streamtype = sd.RawOutputStream if file else sd.OutputStream
                stream = streamtype(
                    samplerate=samplerate,
                    blocksize=blocksize,
                    device=device,
                    channels=channels,
                    dtype='float32',
                    callback=self._play_audio_callback(
                        q=q,
                        blocksize=blocksize,
                        streamtype=streamtype,
                        stream_index=stream_index,
                    ),
                    finished_callback=completed_callback_event.set,
                )

                self.start_playback(stream_index=stream_index, stream=stream)

            with stream:
                # Timeout set until we expect all the buffered blocks to
                # be consumed
                timeout = blocksize * bufsize / samplerate

                while True:
                    while self._get_playback_state(stream_index) == AudioState.PAUSED:
                        self.playback_paused_changed[stream_index].wait()

                    if f:
                        data = f.buffer_read(blocksize, dtype='float32')
                        if not data:
                            break
                    else:
                        duration = mix.duration()
                        blocktime = float(blocksize / samplerate)
                        next_t = (
                            min(t + blocktime, duration)
                            if duration is not None
                            else t + blocktime
                        )

                        data = mix.get_wave(
                            t_start=t, t_end=next_t, samplerate=samplerate
                        )
                        t = next_t

                        if duration is not None and t >= duration:
                            break

                    if self._get_playback_state(stream_index) == AudioState.STOPPED:
                        break

                    try:
                        q.put(data, timeout=timeout)
                    except queue.Full as e:
                        if self._get_playback_state(stream_index) != AudioState.PAUSED:
                            raise e

                completed_callback_event.wait()
        except queue.Full:
            if (
                stream_index is None
                or self._get_playback_state(stream_index) != AudioState.STOPPED
            ):
                self.logger.warning('Playback timeout: audio callback failed?')
        finally:
            if f and not f.closed:
                f.close()

            self.stop_playback([stream_index])

    @action
    def stream_recording(self, *args, **kwargs):
        """
        Deprecated alias for :meth:`.record`.
        """
        warnings.warn(
            'sound.stream_recording is deprecated, use sound.record instead',
            DeprecationWarning,
            stacklevel=1,
        )

        return self.record(*args, **kwargs)

    def create_recorder(
        self,
        device: str,
        output_device: Optional[str] = None,
        fifo: Optional[str] = None,
        outfile: Optional[str] = None,
        duration: Optional[float] = None,
        sample_rate: Optional[int] = None,
        dtype: str = 'int16',
        blocksize: Optional[int] = None,
        latency: Union[float, str] = 'high',
        channels: int = 1,
        redis_queue: Optional[str] = None,
        format: str = 'wav',  # pylint: disable=redefined-builtin
        stream: bool = True,
        play_audio: bool = False,
    ) -> AudioRecorder:
        with self._recorder_locks[device]:
            assert self._recorders.get(device) is None, (
                f'Recording already in progress for device {device}',
            )

            if play_audio:
                output_device = (
                    output_device
                    or self.output_device
                    or self._get_default_device('output')
                )

                device = (device, output_device)  # type: ignore
                input_device = device[0]
            else:
                input_device = device

            if sample_rate is None:
                dev_info = sd.query_devices(device, 'input')
                sample_rate = int(dev_info['default_samplerate'])  # type: ignore

            if blocksize is None:
                blocksize = self.input_blocksize

            if fifo:
                fifo = os.path.expanduser(fifo)
                if os.path.exists(fifo) and stat.S_ISFIFO(os.stat(fifo).st_mode):
                    self.logger.info('Removing previous input stream FIFO %s', fifo)
                    os.unlink(fifo)

                os.mkfifo(fifo, 0o644)
                outfile = fifo
            elif outfile:
                outfile = os.path.expanduser(outfile)

            outfile = outfile or fifo or os.devnull
            self._recorders[input_device] = AudioRecorder(
                plugin=self,
                device=device,
                outfile=outfile,
                duration=duration,
                sample_rate=sample_rate,
                dtype=dtype,
                blocksize=blocksize,
                latency=latency,
                output_format=format,
                channels=channels,
                redis_queue=redis_queue,
                stream=stream,
                audio_pass_through=play_audio,
                should_stop=self._should_stop,
            )

        return self._recorders[input_device]

    def _get_input_device(self, device: Optional[str] = None) -> str:
        return device or self.input_device or self._get_default_device('input')

    @action
    def record(  # pylint: disable=too-many-statements
        self,
        device: Optional[str] = None,
        output_device: Optional[str] = None,
        fifo: Optional[str] = None,
        outfile: Optional[str] = None,
        duration: Optional[float] = None,
        sample_rate: Optional[int] = None,
        dtype: str = 'int16',
        blocksize: Optional[int] = None,
        latency: Union[float, str] = 'high',
        channels: int = 1,
        redis_queue: Optional[str] = None,
        format: str = 'wav',  # pylint: disable=redefined-builtin
        stream: bool = True,
        play_audio: bool = False,
    ):
        """
        Return audio data from an audio source

        :param device: Input device (default: default configured device or
            system default audio input if not configured)
        :param output_device: Audio output device if ``play_audio=True`` (audio
            pass-through) (default: default configured device or system default
            audio output if not configured)
        :param fifo: Path of a FIFO that will be used to exchange audio frames
            with other consumers.
        :param outfile: If specified, the audio data will be persisted on the
            specified audio file too.
        :param duration: Recording duration in seconds (default: record until
            stop event)
        :param sample_rate: Recording sample rate (default: device default rate)
        :param dtype: Data type for the audio samples. Supported types:
            'float64', 'float32', 'int32', 'int16', 'int8', 'uint8'. Default:
            float32
        :param blocksize: Audio block size (default: configured
            `input_blocksize` or 2048)
        :param play_audio: If True, then the recorded audio will be played in
            real-time on the selected ``output_device`` (default: False).
        :param latency: Device latency in seconds (default: the device's default high latency)
        :param channels: Number of channels (default: 1)
        :param redis_queue: If set, the audio chunks will also be published to
            this Redis channel, so other consumers can process them downstream.
        :param format: Audio format. Supported: wav, mp3, ogg, aac. Default: wav.
        :param stream: If True (default), then the audio will be streamed to an
            HTTP endpoint too (default: ``/sound/stream<.format>``).
        """

        device = self._get_input_device(device)
        self.create_recorder(
            device,
            output_device=output_device,
            fifo=fifo,
            outfile=outfile,
            duration=duration,
            sample_rate=sample_rate,
            dtype=dtype,
            blocksize=blocksize,
            latency=latency,
            channels=channels,
            redis_queue=redis_queue,
            format=format,
            stream=stream,
            play_audio=play_audio,
        ).start()

    @action
    def recordplay(self, *args, **kwargs):
        """
        Deprecated alias for :meth:`.record`.
        """
        warnings.warn(
            'sound.recordplay is deprecated, use sound.record with `play_audio=True` instead',
            DeprecationWarning,
            stacklevel=1,
        )

        kwargs['play_audio'] = True
        return self.record(*args, **kwargs)

    @action
    def query_streams(self):
        """
        :returns: A list of active audio streams
        """

        streams = {
            i: {
                attr: getattr(stream, attr)
                for attr in [
                    'active',
                    'closed',
                    'stopped',
                    'blocksize',
                    'channels',
                    'cpu_load',
                    'device',
                    'dtype',
                    'latency',
                    'samplerate',
                    'samplesize',
                ]
                if hasattr(stream, attr)
            }
            for i, stream in self.active_streams.items()
        }

        for i, stream in streams.items():
            stream['playback_state'] = self.playback_state[i].name
            stream['name'] = self.stream_index_to_name.get(i)
            if i in self.stream_mixes:
                stream['mix'] = dict(enumerate(list(self.stream_mixes[i])))

        return streams

    def _get_or_allocate_stream_index(
        self, stream_index=None, stream_name=None, completed_callback_event=None
    ):
        stream = None

        with self.playback_state_lock:
            if stream_index is None:
                if stream_name is not None:
                    stream_index = self.stream_name_to_index.get(stream_name)
            else:
                if stream_name is not None:
                    raise RuntimeError(
                        'Redundant specification of both '
                        + 'stream_name and stream_index'
                    )

            if stream_index is not None:
                stream = self.active_streams.get(stream_index)

            if not stream:
                return (
                    self._allocate_stream_index(
                        stream_name=stream_name,
                        completed_callback_event=completed_callback_event,
                    ),
                    True,
                )

            return stream_index, False

    def _allocate_stream_index(self, stream_name=None, completed_callback_event=None):
        stream_index = None

        with self.playback_state_lock:
            for i in range(len(self.active_streams) + 1):
                if i not in self.active_streams:
                    stream_index = i
                    break

            if stream_index is None:
                raise RuntimeError('No stream index available')

            if stream_name is None:
                stream_name = self._STREAM_NAME_PREFIX + str(stream_index)

            self.active_streams[stream_index] = None
            self.stream_mixes[stream_index] = Mix()
            self.stream_index_to_name[stream_index] = stream_name
            self.stream_name_to_index[stream_name] = stream_index
            self.completed_callback_events[stream_index] = (
                completed_callback_event if completed_callback_event else Event()
            )

        return stream_index

    def start_playback(self, stream_index, stream):
        with self.playback_state_lock:
            self.playback_state[stream_index] = AudioState.RUNNING
            self.active_streams[stream_index] = stream

            if isinstance(self.playback_paused_changed.get(stream_index), Event):
                self.playback_paused_changed[stream_index].clear()
            else:
                self.playback_paused_changed[stream_index] = Event()

        self.logger.info('Playback started on stream index %d', stream_index)

        return stream_index

    @action
    def stop_playback(self, streams=None):
        """
        :param streams: Streams to stop by index or name (default: all)
        :type streams: list[int] or list[str]
        """

        with self.playback_state_lock:
            streams = streams or self.active_streams.keys()
            if not streams:
                return
            completed_callback_events = {}

            for i in streams:
                stream = self.active_streams.get(i)
                if not stream:
                    i = self.stream_name_to_index.get(i)
                    stream = self.active_streams.get(i)
                if not stream:
                    self.logger.info('No such stream index or name: %d', i)
                    continue

                if self.completed_callback_events[i]:
                    completed_callback_events[i] = self.completed_callback_events[i]
                self.playback_state[i] = AudioState.STOPPED

        for i, event in completed_callback_events.items():
            event.wait()

            if i in self.completed_callback_events:
                del self.completed_callback_events[i]
            if i in self.active_streams:
                del self.active_streams[i]
            if i in self.stream_mixes:
                del self.stream_mixes[i]

            if i in self.stream_index_to_name:
                name = self.stream_index_to_name[i]
                del self.stream_index_to_name[i]
                if name in self.stream_name_to_index:
                    del self.stream_name_to_index[name]

        self.logger.info(
            'Playback stopped on streams [%s]',
            ', '.join([str(stream) for stream in completed_callback_events]),
        )

    @action
    def pause_playback(self, streams=None):
        """
        :param streams: Streams to pause by index (default: all)
        :type streams: list[int]
        """

        with self.playback_state_lock:
            streams = streams or self.active_streams.keys()
            if not streams:
                return

            for i in streams:
                stream = self.active_streams.get(i)
                if not stream:
                    i = self.stream_name_to_index.get(i)
                    stream = self.active_streams.get(i)
                if not stream:
                    self.logger.info('No such stream index or name: %d', i)
                    continue

                if self.playback_state[i] == AudioState.PAUSED:
                    self.playback_state[i] = AudioState.RUNNING
                elif self.playback_state[i] == AudioState.RUNNING:
                    self.playback_state[i] = AudioState.PAUSED
                else:
                    continue

                self.playback_paused_changed[i].set()

        self.logger.info(
            'Playback pause toggled on streams [%s]',
            ', '.join([str(stream) for stream in streams]),
        )

    @action
    def stop_recording(
        self, device: Optional[str] = None, timeout: Optional[float] = 2
    ):
        """
        Stop the current recording process on the selected device (default:
        default input device), if it is running.
        """
        device = self._get_input_device(device)
        with self._recorder_locks[device]:
            recorder = self._recorders.pop(device, None)
            if not recorder:
                self.logger.warning('No active recording session for device %s', device)
                return

            recorder.notify_stop()
            recorder.join(timeout=timeout)

    @action
    def pause_recording(self, device: Optional[str] = None):
        """
        Toggle the recording pause state on the selected device (default:
        default input device), if it is running.

        If paused, the recording will be resumed. If running, it will be
        paused. Otherwise, no action will be taken.
        """
        device = self._get_input_device(device)
        with self._recorder_locks[device]:
            recorder = self._recorders.get(device)
            if not recorder:
                self.logger.warning('No active recording session for device %s', device)
                return

            recorder.notify_pause()

    @action
    def release(
        self,
        stream_index=None,
        stream_name=None,
        sound_index=None,
        midi_note=None,
        frequency=None,
    ):
        """
        Remove a sound from an active stream, either by sound index (use
            :meth:`platypush.sound.plugin.SoundPlugin.query_streams` to get
            the sounds playing on the active streams), midi_note, frequency
            or absolute file path.

        :param stream_index: Stream index (default: sound removed from all the
            active streams)
        :type stream_index: int

        :param stream_name: Stream name (default: sound removed from all the
            active streams)
        :type stream_index: str

        :param sound_index: Sound index
        :type sound_index: int

        :param midi_note: MIDI note
        :type midi_note: int

        :param frequency: Sound frequency
        :type frequency: float
        """

        if stream_name:
            if stream_index:
                raise RuntimeError(
                    'stream_index and stream name are ' + 'mutually exclusive'
                )
            stream_index = self.stream_name_to_index.get(stream_name)

        mixes = (
            self.stream_mixes.copy()
            if stream_index is None
            else {stream_index: self.stream_mixes[stream_index]}
        )

        streams_to_stop = []

        for i, mix in mixes.items():
            for j, sound in enumerate(mix):
                if (
                    (sound_index is not None and j == sound_index)
                    or (midi_note is not None and sound.get('midi_note') == midi_note)
                    or (frequency is not None and sound.get('frequency') == frequency)
                ):
                    if len(list(mix)) == 1:
                        # Last sound in the mix
                        streams_to_stop.append(i)
                    else:
                        mix.remove(j)

        if streams_to_stop:
            self.stop_playback(streams_to_stop)

    def _get_playback_state(self, stream_index):
        with self.playback_state_lock:
            return self.playback_state[stream_index]

    @override
    def main(self):
        self.wait_stop()

    @override
    def stop(self):
        super().stop()
        devices = list(self._recorders.keys())

        for device in devices:
            self.stop_recording(device, timeout=0)


# vim:sw=4:ts=4:et:
