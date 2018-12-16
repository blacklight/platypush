"""
.. moduleauthor:: Fabio Manganiello <blacklight86@gmail.com>
"""

import os
import queue
import tempfile
import time

from enum import Enum
from threading import Thread, Event, RLock

from platypush.plugins import Plugin, action


class PlaybackState(Enum):
    STOPPED='STOPPED',
    PLAYING='PLAYING',
    PAUSED='PAUSED'


class RecordingState(Enum):
    STOPPED='STOPPED',
    RECORDING='RECORDING',
    PAUSED='PAUSED'


class SoundPlugin(Plugin):
    """
    Plugin to interact with a sound device.

    Requires:

        * **sounddevice** (``pip install sounddevice``)
        * **soundfile** (``pip install soundfile``)
        * **numpy** (``pip install numpy``)
    """

    _DEFAULT_BLOCKSIZE = 2048
    _DEFAULT_BUFSIZE = 20

    def __init__(self, input_device=None, output_device=None,
                 input_blocksize=_DEFAULT_BLOCKSIZE,
                 output_blocksize=_DEFAULT_BLOCKSIZE,
                 playback_bufsize=_DEFAULT_BUFSIZE, *args, **kwargs):
        """
        :param input_device: Index or name of the default input device. Use :method:`platypush.plugins.sound.query_devices` to get the available devices. Default: system default
        :type input_device: int or str

        :param output_device: Index or name of the default output device. Use :method:`platypush.plugins.sound.query_devices` to get the available devices. Default: system default
        :type output_device: int or str

        :param input_blocksize: Blocksize to be applied to the input device. Try to increase this value if you get input overflow errors while recording. Default: 2048
        :type input_blocksize: int

        :param output_blocksize: Blocksize to be applied to the output device. Try to increase this value if you get output underflow errors while playing. Default: 2048
        :type output_blocksize: int

        :param playback_bufsize: Number of audio blocks that will be cached while playing (default: 20)
        :type playback_bufsize: int
        """

        super().__init__(*args, **kwargs)

        self.input_device = input_device or 0
        self.output_device = output_device or 0
        self.input_blocksize = input_blocksize
        self.output_blocksize = output_blocksize
        self.playback_bufsize = playback_bufsize

        self.playback_state = PlaybackState.STOPPED
        self.playback_state_lock = RLock()
        self.playback_paused_changed = Event()
        self.recording_state = RecordingState.STOPPED
        self.recording_state_lock = RLock()
        self.recording_paused_changed = Event()

    @action
    def query_devices(self, category=None):
        """
        Query the available devices

        :param category: Device category to query. Can be either input or output. Default: None (query all devices)
        :type category: str

        :returns: A dictionary representing the available devices. Example::

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


    @action
    def play(self, file, device=None, blocksize=None, bufsize=_DEFAULT_BUFSIZE):
        """
        Plays a sound file (support formats: wav, raw)

        :param file: Sound file
        :type file: str

        :param device: Output device (default: default configured device or system default audio output if not configured)
        :type device: int or str

        :param blocksize: Audio block size (default: configured `output_blocksize` or 2048)
        :type blocksize: int

        :param bufsize: Size of the audio buffer (default: 20)
        :type bufsize: int
        """

        import sounddevice as sd

        if self._get_playback_state() != PlaybackState.STOPPED:
            self.stop_playback()
            time.sleep(2)

        if blocksize is None:
            blocksize = self.output_blocksize

        self.playback_paused_changed.clear()

        q = queue.Queue(maxsize=bufsize)
        completed_callback_event = Event()
        file = os.path.abspath(os.path.expanduser(file))

        if device is None:
            device = self.output_device

        def audio_callback(outdata, frames, time, status):
            if self._get_playback_state() == PlaybackState.STOPPED:
                raise sd.CallbackAbort

            while self._get_playback_state() == PlaybackState.PAUSED:
                self.playback_paused_changed.wait()

            assert frames == blocksize
            if status.output_underflow:
                self.logger.warning('Output underflow: increase blocksize?')
                outdata = b'\x00' * len(outdata)
                return

            assert not status

            try:
                data = q.get_nowait()
            except queue.Empty:
                self.logger.warning('Buffer is empty: increase buffersize?')
                raise sd.CallbackAbort

            if len(data) < len(outdata):
                outdata[:len(data)] = data
                outdata[len(data):] = b'\x00' * (len(outdata) - len(data))
                raise sd.CallbackStop
            else:
                outdata[:] = data

        try:
            import soundfile as sf

            with sf.SoundFile(file) as f:
                self.start_playback()
                self.logger.info('Started playback of [{}] to device [{}]'.
                                 format(file, device))

                for _ in range(bufsize):
                    data = f.buffer_read(blocksize, dtype='float32')
                    if not data:
                        break

                    while self._get_playback_state() == PlaybackState.PAUSED:
                        self.playback_paused_changed.wait()

                    if self._get_playback_state() == PlaybackState.STOPPED:
                        raise sd.CallbackAbort

                    q.put_nowait(data)

                stream = sd.RawOutputStream(
                    samplerate=f.samplerate, blocksize=blocksize,
                    device=device, channels=f.channels, dtype='float32',
                    callback=audio_callback,
                    finished_callback=completed_callback_event.set)

                with stream:
                    timeout = blocksize * bufsize / f.samplerate
                    while data:
                        while self._get_playback_state() == PlaybackState.PAUSED:
                            self.playback_paused_changed.wait()

                        data = f.buffer_read(blocksize, dtype='float32')

                        if self._get_playback_state() == PlaybackState.STOPPED:
                            raise sd.CallbackAbort

                        try:
                            q.put(data, timeout=timeout)
                        except queue.Full as e:
                            if self._get_playback_state() != PlaybackState.PAUSED:
                                raise e

                    completed_callback_event.wait()
        except queue.Full as e:
            self.logger.warning('Playback timeout: audio callback failed?')
        finally:
            self.stop_playback()


    @action
    def record(self, file=None, duration=None, device=None, sample_rate=None,
               blocksize=None, latency=0, channels=1, subtype='PCM_24'):
        """
        Records audio to a sound file (support formats: wav, raw)

        :param file: Sound file (default: the method will create a temporary file with the recording)
        :type file: str

        :param duration: Recording duration in seconds (default: record until stop event)
        :type duration: float

        :param device: Input device (default: default configured device or system default audio input if not configured)
        :type device: int or str

        :param sample_rate: Recording sample rate (default: device default rate)
        :type sample_rate: int

        :param blocksize: Audio block size (default: configured `input_blocksize` or 2048)
        :type blocksize: int

        :param latency: Device latency in seconds (default: 0)
        :type latency: float

        :param channels: Number of channels (default: 1)
        :type channels: int

        :param subtype: Recording subtype - see `soundfile docs <https://pysoundfile.readthedocs.io/en/0.9.0/#soundfile.available_subtypes>`_ for a list of the available subtypes (default: PCM_24)
        :type subtype: str
        """

        import sounddevice as sd

        if self._get_recording_state() != RecordingState.STOPPED:
            self.stop_recording()
            time.sleep(2)

        self.recording_paused_changed.clear()

        if file:
            file = os.path.abspath(os.path.expanduser(file))
        else:
            file = tempfile.mktemp(prefix='platypush_recording_', suffix='.wav',
                                   dir='')

        if os.path.isfile(file):
            os.unlink(file)

        if device is None:
            device = self.input_device

        if sample_rate is None:
            dev_info = sd.query_devices(device, 'input')
            sample_rate = int(dev_info['default_samplerate'])

        if blocksize is None:
            blocksize = self.input_blocksize

        q = queue.Queue()

        def audio_callback(indata, frames, time, status):
            while self._get_recording_state() == RecordingState.PAUSED:
                self.recording_paused_changed.wait()

            if status:
                self.logger.warning('Recording callback status: {}'.format(
                    str(status)))

            q.put(indata.copy())


        try:
            import soundfile as sf
            import numpy

            with sf.SoundFile(file, mode='x', samplerate=sample_rate,
                              channels=channels, subtype=subtype) as f:
                with sd.InputStream(samplerate=sample_rate, device=device,
                                    channels=channels, callback=audio_callback,
                                    latency=latency, blocksize=blocksize):
                    self.start_recording()
                    self.logger.info('Started recording from device [{}] to [{}]'.
                                    format(device, file))

                    recording_started_time = time.time()

                    while self._get_recording_state() != RecordingState.STOPPED \
                            and (duration is None or
                                 time.time() - recording_started_time < duration):
                        while self._get_recording_state() == RecordingState.PAUSED:
                            self.recording_paused_changed.wait()

                        get_args = {
                            'block': True,
                            'timeout': max(0, duration - (time.time() -
                                                          recording_started_time))
                        } if duration is not None else {}

                        data = q.get(**get_args)
                        f.write(data)

                f.flush()

        except queue.Empty as e:
            self.logger.warning('Recording timeout: audio callback failed?')
        finally:
            self.stop_recording()


    @action
    def recordplay(self, duration=None, input_device=None, output_device=None,
                   sample_rate=None, blocksize=None, latency=0, channels=1,
                   dtype=None):
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

        :param dtype: Data type for the recording - see `soundfile docs <https://python-sounddevice.readthedocs.io/en/0.3.12/_modules/sounddevice.html#rec>`_ for available types (default: input device default)
        :type dtype: str
        """

        import sounddevice as sd

        if self._get_playback_state() != PlaybackState.STOPPED:
            self.stop_playback()
            time.sleep(2)

        if self._get_recording_state() != RecordingState.STOPPED:
            self.stop_recording()
            time.sleep(2)

        self.playback_paused_changed.clear()
        self.recording_paused_changed.clear()

        if input_device is None:
            input_device = self.input_device

        if output_device is None:
            output_device = self.output_device

        if sample_rate is None:
            dev_info = sd.query_devices(input_device, 'input')
            sample_rate = int(dev_info['default_samplerate'])

        if blocksize is None:
            blocksize = self.output_blocksize

        def audio_callback(indata, outdata, frames, time, status):
            while self._get_recording_state() == RecordingState.PAUSED:
                self.recording_paused_changed.wait()

            if status:
                self.logger.warning('Recording callback status: {}'.format(
                    str(status)))

            outdata[:] = indata


        try:
            import soundfile as sf
            import numpy

            with sd.Stream(samplerate=sample_rate, channels=channels,
                           blocksize=blocksize, latency=latency,
                           device=(input_device, output_device),
                           dtype=dtype, callback=audio_callback):
                self.start_recording()
                self.start_playback()

                self.logger.info('Started recording pass-through from device ' +
                                 '[{}] to device [{}]'.
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
            self.stop_playback()
            self.stop_recording()


    def start_playback(self):
        with self.playback_state_lock:
            self.playback_state = PlaybackState.PLAYING

    @action
    def stop_playback(self):
        with self.playback_state_lock:
            self.playback_state = PlaybackState.STOPPED
        self.logger.info('Playback stopped')

    @action
    def pause_playback(self):
        with self.playback_state_lock:
            if self.playback_state == PlaybackState.PAUSED:
                self.playback_state = PlaybackState.PLAYING
            elif self.playback_state == PlaybackState.PLAYING:
                self.playback_state = PlaybackState.PAUSED
            else:
                return

        self.logger.info('Playback paused state toggled')
        self.playback_paused_changed.set()

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

    def _get_playback_state(self):
        with self.playback_state_lock:
            return self.playback_state

    def _get_recording_state(self):
        with self.recording_state_lock:
            return self.recording_state

    @action
    def get_state(self):
        return {
            'playback_state': self._get_playback_state().name,
            'recording_state': self._get_recording_state().name,
        }


# vim:sw=4:ts=4:et:

