"""
.. moduleauthor:: Fabio Manganiello <blacklight86@gmail.com>
"""

import os
import queue
import stat
import tempfile
import time

from enum import Enum
from threading import Thread, Event, RLock

from .core import Sound, Mix

from platypush.context import get_bus
from platypush.message.event.sound import \
    SoundRecordingStartedEvent, SoundRecordingStoppedEvent

from platypush.plugins import Plugin, action


class PlaybackState(Enum):
    STOPPED = 'STOPPED',
    PLAYING = 'PLAYING',
    PAUSED = 'PAUSED'


class RecordingState(Enum):
    STOPPED = 'STOPPED',
    RECORDING = 'RECORDING',
    PAUSED = 'PAUSED'


class SoundPlugin(Plugin):
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
    """

    _STREAM_NAME_PREFIX = 'platypush-stream-'
    _default_input_stream_fifo = os.path.join(tempfile.gettempdir(), 'inputstream')

    # noinspection PyProtectedMember
    def __init__(self, input_device=None, output_device=None,
                 input_blocksize=Sound._DEFAULT_BLOCKSIZE,
                 output_blocksize=Sound._DEFAULT_BLOCKSIZE, **kwargs):
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
        self.recording_state = RecordingState.STOPPED
        self.recording_state_lock = RLock()
        self.recording_paused_changed = Event()
        self.active_streams = {}
        self.stream_name_to_index = {}
        self.stream_index_to_name = {}
        self.completed_callback_events = {}

    @staticmethod
    def _get_default_device(category):
        """
        Query the default audio devices.

        :param category: Device category to query. Can be either input or output
        :type category: str
        """

        import sounddevice as sd
        return sd.query_hostapis()[0].get('default_' + category.lower() + '_device')

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

        import sounddevice as sd

        devs = sd.query_devices()
        if category == 'input':
            devs = [d for d in devs if d.get('max_input_channels') > 0]
        elif category == 'output':
            devs = [d for d in devs if d.get('max_output_channels') > 0]

        return devs

    def _play_audio_callback(self, q, blocksize, streamtype, stream_index):
        import sounddevice as sd

        is_raw_stream = streamtype == sd.RawOutputStream

        # noinspection PyUnusedLocal
        def audio_callback(outdata, frames, frame_time, status):
            if self._get_playback_state(stream_index) == PlaybackState.STOPPED:
                raise sd.CallbackStop

            while self._get_playback_state(stream_index) == PlaybackState.PAUSED:
                self.playback_paused_changed[stream_index].wait()

            if frames != blocksize:
                self.logger.warning('Received {} frames, expected blocksize is {}'.
                                    format(frames, blocksize))
                return

            if status.output_underflow:
                self.logger.warning('Output underflow: increase blocksize?')
                outdata = (b'\x00' if is_raw_stream else 0.) * len(outdata)
                return

            if status:
                self.logger.warning('Audio callback failed: {}'.format(status))

            try:
                data = q.get_nowait()
            except queue.Empty:
                self.logger.warning('Buffer is empty: increase buffersize?')
                raise sd.CallbackStop

            if len(data) < len(outdata):
                outdata[:len(data)] = data
                outdata[len(data):] = (b'\x00' if is_raw_stream else 0.) * \
                                      (len(outdata) - len(data))
            else:
                outdata[:] = data

        return audio_callback

    @action
    def play(self, file=None, sound=None, device=None, blocksize=None,
             bufsize=None, samplerate=None, channels=None, stream_name=None,
             stream_index=None):
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
            raise RuntimeError('Please specify either a file to play or a ' +
                               'list of sound objects')

        import sounddevice as sd

        if blocksize is None:
            blocksize = self.output_blocksize

        if bufsize is None:
            if file:
                bufsize = Sound._DEFAULT_FILE_BUFSIZE
            else:
                bufsize = Sound._DEFAULT_SYNTH_BUFSIZE

        q = queue.Queue(maxsize=bufsize)
        f = None
        t = 0.

        if file:
            file = os.path.abspath(os.path.expanduser(file))

        if device is None:
            device = self.output_device
        if device is None:
            device = self._get_default_device('output')

        if file:
            import soundfile as sf
            f = sf.SoundFile(file)
        if not samplerate:
            samplerate = f.samplerate if f else Sound._DEFAULT_SAMPLERATE
        if not channels:
            channels = f.channels if f else 1

        mix = None
        with self.playback_state_lock:
            stream_index, is_new_stream = self._get_or_allocate_stream_index(
                stream_index=stream_index, stream_name=stream_name)

            if sound and stream_index in self.stream_mixes:
                mix = self.stream_mixes[stream_index]
                mix.add(sound)

        if not mix:
            return None, "Unable to allocate the stream"

        self.logger.info(('Starting playback of {} to sound device [{}] ' +
                          'on stream [{}]').format(
            file or sound, device, stream_index))

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
                    next_t = min(t + blocktime, duration) \
                        if duration is not None else t + blocktime

                    data = mix.get_wave(t_start=t, t_end=next_t, samplerate=samplerate)
                    t = next_t

                    if duration is not None and t >= duration:
                        break

                q.put_nowait(data)  # Pre-fill the audio queue

            stream = self.active_streams[stream_index]
            completed_callback_event = self.completed_callback_events[stream_index]

            if stream is None:
                streamtype = sd.RawOutputStream if file else sd.OutputStream
                stream = streamtype(samplerate=samplerate, blocksize=blocksize,
                                    device=device, channels=channels,
                                    dtype='float32',
                                    callback=self._play_audio_callback(
                                        q=q, blocksize=blocksize,
                                        streamtype=streamtype,
                                        stream_index=stream_index),
                                    finished_callback=completed_callback_event.set)

                self._start_playback(stream_index=stream_index, stream=stream)

            with stream:
                # Timeout set until we expect all the buffered blocks to
                # be consumed
                timeout = blocksize * bufsize / samplerate

                while True:
                    while self._get_playback_state(stream_index) == \
                            PlaybackState.PAUSED:
                        self.playback_paused_changed[stream_index].wait()

                    if f:
                        data = f.buffer_read(blocksize, dtype='float32')
                        if not data:
                            break
                    else:
                        duration = mix.duration()
                        blocktime = float(blocksize / samplerate)
                        next_t = min(t + blocktime, duration) \
                            if duration is not None else t + blocktime

                        data = mix.get_wave(t_start=t, t_end=next_t,
                                            samplerate=samplerate)
                        t = next_t

                        if duration is not None and t >= duration:
                            break

                    if self._get_playback_state(stream_index) == \
                            PlaybackState.STOPPED:
                        break

                    try:
                        q.put(data, timeout=timeout)
                    except queue.Full as e:
                        if self._get_playback_state(stream_index) != \
                                PlaybackState.PAUSED:
                            raise e

                completed_callback_event.wait()
        except queue.Full as e:
            if stream_index is None or \
                    self._get_playback_state(stream_index) != PlaybackState.STOPPED:
                self.logger.warning('Playback timeout: audio callback failed?')
        finally:
            if f and not f.closed:
                f.close()
                f = None

            self.stop_playback([stream_index])

    @action
    def stream_recording(self, device=None, fifo=None, duration=None, sample_rate=None,
                         dtype='float32', blocksize=None, latency=0, channels=1):
        """
        Return audio data from an audio source

        :param device: Input device (default: default configured device or system default audio input if not configured)
        :type device: int or str

        :param fifo: Path of the FIFO that will be used to exchange audio samples (default: /tmp/inputstream)
        :type fifo: str

        :param duration: Recording duration in seconds (default: record until stop event)
        :type duration: float

        :param sample_rate: Recording sample rate (default: device default rate)
        :type sample_rate: int

        :param dtype: Data type for the audio samples. Supported types:
            'float64', 'float32', 'int32', 'int16', 'int8', 'uint8'. Default: float32
        :type dtype: str

        :param blocksize: Audio block size (default: configured `input_blocksize` or 2048)
        :type blocksize: int

        :param latency: Device latency in seconds (default: 0)
        :type latency: float

        :param channels: Number of channels (default: 1)
        :type channels: int
        """

        import sounddevice as sd

        self.recording_paused_changed.clear()

        if device is None:
            device = self.input_device
        if device is None:
            device = self._get_default_device('input')

        if sample_rate is None:
            dev_info = sd.query_devices(device, 'input')
            sample_rate = int(dev_info['default_samplerate'])

        if blocksize is None:
            blocksize = self.input_blocksize

        if not fifo:
            fifo = self._default_input_stream_fifo

        q = queue.Queue()

        # noinspection PyUnusedLocal
        def audio_callback(indata, frames, time_duration, status):
            while self._get_recording_state() == RecordingState.PAUSED:
                self.recording_paused_changed.wait()

            if status:
                self.logger.warning('Recording callback status: {}'.format(str(status)))

            q.put(indata.copy())

        def streaming_thread():
            try:
                with sd.InputStream(samplerate=sample_rate, device=device,
                                    channels=channels, callback=audio_callback,
                                    dtype=dtype, latency=latency, blocksize=blocksize):
                    with open(fifo, 'wb') as audio_queue:
                        self.start_recording()
                        get_bus().post(SoundRecordingStartedEvent())
                        self.logger.info('Started recording from device [{}]'.format(device))
                        recording_started_time = time.time()

                        while self._get_recording_state() != RecordingState.STOPPED \
                                and (duration is None or
                                     time.time() - recording_started_time < duration):
                            while self._get_recording_state() == RecordingState.PAUSED:
                                self.recording_paused_changed.wait()

                            get_args = {
                                'block': True,
                                'timeout': max(0, duration - (time.time() - recording_started_time)),
                            } if duration is not None else {}

                            data = q.get(**get_args)
                            if not len(data):
                                continue

                            audio_queue.write(data)
            except queue.Empty:
                self.logger.warning('Recording timeout: audio callback failed?')
            finally:
                self.stop_recording()
                get_bus().post(SoundRecordingStoppedEvent())

        if os.path.exists(fifo):
            if stat.S_ISFIFO(os.stat(fifo).st_mode):
                self.logger.info('Removing previous input stream FIFO {}'.format(fifo))
                os.unlink(fifo)
            else:
                raise RuntimeError('{} exists and is not a FIFO. Please remove it or rename it'.format(fifo))

        os.mkfifo(fifo, 0o644)
        Thread(target=streaming_thread).start()

    @action
    def record(self, outfile=None, duration=None, device=None, sample_rate=None,
               format=None, blocksize=None, latency=0, channels=1, subtype='PCM_24'):
        """
        Records audio to a sound file (support formats: wav, raw)

        :param outfile: Sound file (default: the method will create a temporary file with the recording)
        :type outfile: str

        :param duration: Recording duration in seconds (default: record until stop event)
        :type duration: float

        :param device: Input device (default: default configured device or system default audio input if not configured)
        :type device: int or str

        :param sample_rate: Recording sample rate (default: device default rate)
        :type sample_rate: int

        :param format: Audio format (default: WAV)
        :type format: str

        :param blocksize: Audio block size (default: configured `input_blocksize` or 2048)
        :type blocksize: int

        :param latency: Device latency in seconds (default: 0)
        :type latency: float

        :param channels: Number of channels (default: 1)
        :type channels: int

        :param subtype: Recording subtype - see `Soundfile docs - Subtypes <https://pysoundfile.readthedocs.io/en/0.9.0/#soundfile.available_subtypes>`_ for a list of the available subtypes (default: PCM_24)
        :type subtype: str
        """

        def recording_thread(outfile, duration, device, sample_rate, format,
                             blocksize, latency, channels, subtype):
            import sounddevice as sd

            self.recording_paused_changed.clear()

            if outfile:
                outfile = os.path.abspath(os.path.expanduser(outfile))
                if os.path.isfile(outfile):
                    self.logger.info('Removing existing audio file {}'.format(outfile))
                    os.unlink(outfile)
            else:
                outfile = tempfile.NamedTemporaryFile(
                    prefix='recording_', suffix='.wav', delete=False,
                    dir=tempfile.gettempdir()).name

            if device is None:
                device = self.input_device
            if device is None:
                device = self._get_default_device('input')

            if sample_rate is None:
                dev_info = sd.query_devices(device, 'input')
                sample_rate = int(dev_info['default_samplerate'])

            if blocksize is None:
                blocksize = self.input_blocksize

            q = queue.Queue()

            def audio_callback(indata, frames, duration, status):
                while self._get_recording_state() == RecordingState.PAUSED:
                    self.recording_paused_changed.wait()

                if status:
                    self.logger.warning('Recording callback status: {}'.format(
                        str(status)))

                q.put({
                    'timestamp': time.time(),
                    'frames': frames,
                    'time': duration,
                    'data': indata.copy()
                })

            try:
                import soundfile as sf
                import numpy

                with sf.SoundFile(outfile, mode='w', samplerate=sample_rate,
                                  format=format, channels=channels, subtype=subtype) as f:
                    with sd.InputStream(samplerate=sample_rate, device=device,
                                        channels=channels, callback=audio_callback,
                                        latency=latency, blocksize=blocksize):
                        self.start_recording()
                        get_bus().post(SoundRecordingStartedEvent(filename=outfile))
                        self.logger.info('Started recording from device [{}] to [{}]'.
                                         format(device, outfile))

                        recording_started_time = time.time()

                        while self._get_recording_state() != RecordingState.STOPPED \
                                and (duration is None or
                                     time.time() - recording_started_time < duration):
                            while self._get_recording_state() == RecordingState.PAUSED:
                                self.recording_paused_changed.wait()

                            get_args = {
                                'block': True,
                                'timeout': max(0, duration - (time.time() - recording_started_time)),
                            } if duration is not None else {}

                            data = q.get(**get_args)
                            if data and time.time() - data.get('timestamp') <= 1.0:
                                # Only write the block if the latency is still acceptable
                                f.write(data['data'])

                    f.flush()

            except queue.Empty:
                self.logger.warning('Recording timeout: audio callback failed?')
            finally:
                self.stop_recording()
                get_bus().post(SoundRecordingStoppedEvent(filename=outfile))

        Thread(target=recording_thread,
               args=(
                   outfile, duration, device, sample_rate, format, blocksize, latency, channels, subtype)
               ).start()

    @action
    def recordplay(self, duration=None, input_device=None, output_device=None,
                   sample_rate=None, blocksize=None, latency=0, channels=1, dtype=None):
        """
        Records audio and plays it on an output sound device (audio pass-through)

        :param duration: Recording duration in seconds (default: record until stop event)
        :type duration: float

        :param input_device: Input device (default: default configured device or system default audio input if not configured)
        :type input_device: int or str

        :param output_device: Output device (default: default configured device or system default audio output if not configured)
        :type output_device: int or str

        :param sample_rate: Recording sample rate (default: device default rate)
        :type sample_rate: int

        :param blocksize: Audio block size (default: configured `output_blocksize` or 2048)
        :type blocksize: int

        :param latency: Device latency in seconds (default: 0)
        :type latency: float

        :param channels: Number of channels (default: 1)
        :type channels: int

        :param dtype: Data type for the recording - see `Soundfile docs - Recording <https://python-sounddevice.readthedocs.io/en/0.3.12/_modules/sounddevice.html#rec>`_ for available types (default: input device default)
        :type dtype: str
        """

        import sounddevice as sd

        self.recording_paused_changed.clear()

        if input_device is None:
            input_device = self.input_device
        if input_device is None:
            input_device = self._get_default_device('input')

        if output_device is None:
            output_device = self.output_device
        if output_device is None:
            output_device = self._get_default_device('output')

        if sample_rate is None:
            dev_info = sd.query_devices(input_device, 'input')
            sample_rate = int(dev_info['default_samplerate'])

        if blocksize is None:
            blocksize = self.output_blocksize

        # noinspection PyUnusedLocal
        def audio_callback(indata, outdata, frames, time, status):
            while self._get_recording_state() == RecordingState.PAUSED:
                self.recording_paused_changed.wait()

            if status:
                self.logger.warning('Recording callback status: {}'.format(
                    str(status)))

            outdata[:] = indata

        stream_index = None

        try:
            import soundfile as sf
            import numpy

            stream_index = self._allocate_stream_index()
            stream = sd.Stream(samplerate=sample_rate, channels=channels,
                               blocksize=blocksize, latency=latency,
                               device=(input_device, output_device),
                               dtype=dtype, callback=audio_callback)
            self.start_recording()
            self._start_playback(stream_index=stream_index,
                                 stream=stream)

            self.logger.info('Started recording pass-through from device ' +
                             '[{}] to sound device [{}]'.
                             format(input_device, output_device))

            recording_started_time = time.time()

            while self._get_recording_state() != RecordingState.STOPPED \
                    and (duration is None or
                         time.time() - recording_started_time < duration):
                while self._get_recording_state() == RecordingState.PAUSED:
                    self.recording_paused_changed.wait()

                time.sleep(0.1)

        except queue.Empty as e:
            self.logger.warning('Recording timeout: audio callback failed?')
        finally:
            self.stop_playback([stream_index])
            self.stop_recording()

    @action
    def query_streams(self):
        """
        :returns: A list of active audio streams
        """

        streams = {
            i: {
                attr: getattr(stream, attr)
                for attr in ['active', 'closed', 'stopped', 'blocksize',
                             'channels', 'cpu_load', 'device', 'dtype',
                             'latency', 'samplerate', 'samplesize']
                if hasattr(stream, attr)
            } for i, stream in self.active_streams.items()
        }

        for i, stream in streams.items():
            stream['playback_state'] = self.playback_state[i].name
            stream['name'] = self.stream_index_to_name.get(i)
            if i in self.stream_mixes:
                stream['mix'] = {j: sound for j, sound in
                                 enumerate(list(self.stream_mixes[i]))}

        return streams

    def _get_or_allocate_stream_index(self, stream_index=None, stream_name=None,
                                      completed_callback_event=None):
        stream = None

        with self.playback_state_lock:
            if stream_index is None:
                if stream_name is not None:
                    stream_index = self.stream_name_to_index.get(stream_name)
            else:
                if stream_name is not None:
                    raise RuntimeError('Redundant specification of both ' +
                                       'stream_name and stream_index')

            if stream_index is not None:
                stream = self.active_streams.get(stream_index)

            if not stream:
                return (self._allocate_stream_index(stream_name=stream_name,
                                                    completed_callback_event=
                                                    completed_callback_event),
                        True)

            return (stream_index, False)

    def _allocate_stream_index(self, stream_name=None,
                               completed_callback_event=None):
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
            self.completed_callback_events[stream_index] = \
                completed_callback_event if completed_callback_event else Event()

        return stream_index

    def _start_playback(self, stream_index, stream):
        with self.playback_state_lock:
            self.playback_state[stream_index] = PlaybackState.PLAYING
            self.active_streams[stream_index] = stream

            if isinstance(self.playback_paused_changed.get(stream_index), Event):
                self.playback_paused_changed[stream_index].clear()
            else:
                self.playback_paused_changed[stream_index] = Event()

        self.logger.info('Playback started on stream index {}'.
                         format(stream_index))

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
                    self.logger.info('No such stream index or name: {}'.
                                     format(i))
                    continue

                if self.completed_callback_events[i]:
                    completed_callback_events[i] = self.completed_callback_events[i]
                self.playback_state[i] = PlaybackState.STOPPED

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

        self.logger.info('Playback stopped on streams [{}]'.format(
            ', '.join([str(stream) for stream in
                       completed_callback_events.keys()])))

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
                    self.logger.info('No such stream index or name: {}'.
                                     format(i))
                    continue

                stream = self.active_streams[i]
                if self.playback_state[i] == PlaybackState.PAUSED:
                    self.playback_state[i] = PlaybackState.PLAYING
                elif self.playback_state[i] == PlaybackState.PLAYING:
                    self.playback_state[i] = PlaybackState.PAUSED
                else:
                    continue

                self.playback_paused_changed[i].set()

        self.logger.info('Playback pause toggled on streams [{}]'.format(
            ', '.join([str(stream) for stream in streams])))

    def start_recording(self):
        with self.recording_state_lock:
            self.recording_state = RecordingState.RECORDING

    @action
    def stop_recording(self):
        with self.recording_state_lock:
            self.recording_state = RecordingState.STOPPED
        self.logger.info('Recording stopped')

    @action
    def pause_recording(self):
        with self.recording_state_lock:
            if self.recording_state == RecordingState.PAUSED:
                self.recording_state = RecordingState.RECORDING
            elif self.recording_state == RecordingState.RECORDING:
                self.recording_state = RecordingState.PAUSED
            else:
                return

        self.logger.info('Recording paused state toggled')
        self.recording_paused_changed.set()

    @action
    def release(self, stream_index=None, stream_name=None,
                sound_index=None, midi_note=None, frequency=None):
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
                raise RuntimeError('stream_index and stream name are ' +
                                   'mutually exclusive')
            stream_index = self.stream_name_to_index.get(stream_name)

        mixes = {
            i: mix for i, mix in self.stream_mixes.items()
        } if stream_index is None else {
            stream_index: self.stream_mixes[stream_index]
        }

        streams_to_stop = []

        for i, mix in mixes.items():
            for j, sound in enumerate(mix):
                if (sound_index is not None and j == sound_index) or \
                        (midi_note is not None
                         and sound.get('midi_note') == midi_note) or \
                        (frequency is not None
                         and sound.get('frequency') == frequency):
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

    def _get_recording_state(self):
        with self.recording_state_lock:
            return self.recording_state


# vim:sw=4:ts=4:et:
