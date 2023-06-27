from dataclasses import asdict
import warnings
from typing import Iterable, List, Optional, Union
from typing_extensions import override

from platypush.plugins import RunnablePlugin, action

from ._manager import AudioManager
from ._model import DeviceType, StreamType


class SoundPlugin(RunnablePlugin):
    """
    Plugin to interact with a sound device.

    Among the other features, enabling this plugin allows you to stream audio
    over HTTP from the device where the application is running, if
    :class:`platypush.backend.http.HttpBackend` is enabled.

    Simply open
    ``http://<host>:<backend-port>/sound/stream.[mp3|wav|acc|ogg]?token=<your-token>``
    to access live recording from the audio device.

    It can also be used as a general-purpose audio player and synthesizer,
    supporting both local and remote audio resources, as well as a MIDI-like
    interface through the :meth:`.play` command.

    Triggers:

        * :class:`platypush.message.event.sound.SoundPlaybackStartedEvent` on playback start
        * :class:`platypush.message.event.sound.SoundPlaybackStoppedEvent` on playback stop
        * :class:`platypush.message.event.sound.SoundPlaybackPausedEvent` on playback pause
        * :class:`platypush.message.event.sound.SoundPlaybackResumedEvent` on playback resume
        * :class:`platypush.message.event.sound.SoundRecordingStartedEvent` on recording start
        * :class:`platypush.message.event.sound.SoundRecordingStoppedEvent` on recording stop
        * :class:`platypush.message.event.sound.SoundRecordingPausedEvent` on recording pause
        * :class:`platypush.message.event.sound.SoundRecordingResumedEvent` on recording resume

    Requires:

        * **sounddevice** (``pip install sounddevice``)
        * **numpy** (``pip install numpy``)
        * **ffmpeg** package installed on the system
        * **portaudio** package installed on the system - either
          ``portaudio19-dev`` on Debian-like systems, or ``portaudio`` on Arch.

    """

    _DEFAULT_BLOCKSIZE = 1024
    _DEFAULT_QUEUE_SIZE = 10

    def __init__(
        self,
        input_device: Optional[DeviceType] = None,
        output_device: Optional[DeviceType] = None,
        input_blocksize: int = _DEFAULT_BLOCKSIZE,
        output_blocksize: int = _DEFAULT_BLOCKSIZE,
        queue_size: Optional[int] = _DEFAULT_QUEUE_SIZE,
        ffmpeg_bin: str = 'ffmpeg',
        **kwargs,
    ):
        """
        :param input_device: Index or name of the default input device. Use
            :meth:`platypush.plugins.sound.query_devices` to get the
            available devices. Default: system default
        :param output_device: Index or name of the default output device.
            Use :meth:`platypush.plugins.sound.query_devices` to get the
            available devices. Default: system default
        :param input_blocksize: Blocksize to be applied to the input device.
            Try to increase this value if you get input overflow errors while
            recording. Default: 1024
        :param output_blocksize: Blocksize to be applied to the output device.
            Try to increase this value if you get output underflow errors while
            playing. Default: 1024
        :param queue_size: When running in synth mode, this is the maximum
            number of generated audio frames that will be queued before the
            audio device processes them (default: 100).
        :param ffmpeg_bin: Path of the ``ffmpeg`` binary (default: search for
            the ``ffmpeg`` in the ``PATH``).
        """

        super().__init__(**kwargs)

        self.input_device = input_device
        self.output_device = output_device
        self.input_blocksize = input_blocksize
        self.output_blocksize = output_blocksize
        self.ffmpeg_bin = ffmpeg_bin
        self._manager = AudioManager(
            input_blocksize=self.input_blocksize,
            output_blocksize=self.output_blocksize,
            should_stop=self._should_stop,
            input_device=input_device,
            output_device=output_device,
            queue_size=queue_size,
        )

    @action
    def play(
        self,
        resource: Optional[str] = None,
        file: Optional[str] = None,
        sound: Optional[Union[dict, Iterable[dict]]] = None,
        device: Optional[DeviceType] = None,
        duration: Optional[float] = None,
        blocksize: Optional[int] = None,
        sample_rate: Optional[int] = None,
        channels: int = 2,
        volume: float = 100,
        stream_name: Optional[str] = None,
        stream_index: Optional[int] = None,
    ):
        """
        Plays an audio file/URL (any audio format supported by ffmpeg works) or
        a synthetic sound.

        :param resource: Audio resource to be played. It can be a local file or
            a URL.
        :param file: **Deprecated**. Use ``resource`` instead.
        :param sound: Sound to play. Specify this if you want to play
            synthetic sounds. You can also create polyphonic sounds by just
            calling play multiple times. Frequencies can be specified either by
            ``midi_note`` - either as strings (e.g. ``A4``) or integers (e.g.
            ``69``) - or by ``frequency`` (e.g. ``440`` for 440 Hz). You can
            also specify a list of sounds here if you want to apply multiple
            harmonics on a base sound.
            Some examples:

                .. code-block:: python

                    {
                        "frequency": 440,  # 440 Hz
                        "volume":    100,  # Maximum volume
                        "duration":  1.0   # 1 second or until stop_playback
                    }

                .. code-block:: python

                    [
                        {
                            "midi_note": "A4", # A @ 440 Hz
                            "volume":    100,  # Maximum volume
                            "duration":  1.0   # 1 second or until stop_playback
                        },
                        {
                            "midi_note": "E5", # Play the harmonic one fifth up
                            "volume":    25,   # 1/4 of the volume
                            "duration":  1.0   # 1 second or until stop_playback
                            "phase":     3.14  # ~180 degrees phase
                            # Make it a triangular wave (default: sin).
                            # Supported types: "sin", "triang", "square",
                            # "sawtooth"
                            "shape:      "triang"
                        }
                    ]

                .. code-block:: python

                    [
                        {
                            "midi_note": "C4", # C4 MIDI note
                            "duration":  0.5   # 0.5 seconds or until stop_playback
                        },
                        {
                            "midi_note": "G5", # G5 MIDI note
                            "duration":  0.5,  # 0.5 seconds or until stop_playback
                            "delay":     0.5   # Start this note 0.5 seconds
                                               # after playback has started
                        }
                    ]

        :param device: Output device (default: default configured device or
            system default audio output if not configured)
        :param duration: Playback duration, in seconds. Default: None - play
            until the end of the audio source or until :meth:`.stop_playback`.
        :param blocksize: Audio block size (default: configured
            `output_blocksize` or 2048)
        :param sample_rate: Audio sample rate. Default: audio file sample rate
            if in file mode, 44100 Hz if in synth mode
        :param channels: Number of audio channels. Default: number of channels
            in the audio file in file mode, 1 if in synth mode
        :param volume: Playback volume, between 0 and 100. Default: 100.
        :param stream_index: If specified, play to an already active stream
            index (you can get them through
            :meth:`platypush.plugins.sound.query_streams`). Default:
            creates a new audio stream through PortAudio.
        :param stream_name: Name of the stream to play to. If set, the sound
            will be played to the specified stream name, or a stream with that
            name will be created. If not set, and ``stream_index`` is not set
            either, then a new stream will be created on the next available
            index and named ``platypush-stream-<index>``.
        """

        dev = self._manager.get_device(device=device, type=StreamType.OUTPUT)
        blocksize = blocksize or self.output_blocksize

        if file:
            warnings.warn(
                'file is deprecated, use resource instead',
                DeprecationWarning,
                stacklevel=1,
            )
            if not resource:
                resource = file

        if not (resource or sound):
            raise RuntimeError(
                'Please specify either a file to play or a list of sound objects'
            )

        self.logger.info(
            'Starting playback of %s to sound device [%s] on stream [%s]',
            resource or sound,
            dev.index,
            stream_index,
        )

        self._manager.create_player(
            device=dev.index,
            infile=resource,
            sound=sound,
            duration=duration,
            blocksize=blocksize,
            sample_rate=sample_rate,
            channels=channels,
            volume=volume,
            stream_name=stream_name,
        ).start()

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

    @action
    def record(
        self,
        device: Optional[DeviceType] = None,
        output_device: Optional[DeviceType] = None,
        fifo: Optional[str] = None,
        outfile: Optional[str] = None,
        duration: Optional[float] = None,
        sample_rate: Optional[int] = None,
        dtype: str = 'int16',
        blocksize: Optional[int] = None,
        latency: Union[float, str] = 'high',
        channels: int = 1,
        volume: float = 100,
        redis_queue: Optional[str] = None,
        format: str = 'wav',  # pylint: disable=redefined-builtin
        stream: bool = True,
        stream_name: Optional[str] = None,
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
        :param volume: Recording volume, between 0 and 100. Default: 100.
        :param redis_queue: If set, the audio chunks will also be published to
            this Redis channel, so other consumers can process them downstream.
        :param format: Audio format. Supported: wav, mp3, ogg, aac, flac.
            Default: wav.
        :param stream: If True (default), then the audio will be streamed to an
            HTTP endpoint too (default: ``/sound/stream<.format>``).
        :param stream_name: Custom name for the output stream.
        """

        dev = self._manager.get_device(device=device, type=StreamType.INPUT)
        self._manager.create_recorder(
            dev.index,
            output_device=output_device,
            fifo=fifo,
            outfile=outfile,
            duration=duration,
            sample_rate=sample_rate,
            dtype=dtype,
            blocksize=blocksize,
            latency=latency,
            channels=channels,
            volume=volume,
            redis_queue=redis_queue,
            format=format,
            stream=stream,
            stream_name=stream_name,
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
    def status(self) -> List[dict]:
        """
        :return: The current status of the audio devices and streams.

        Example:

            .. code-block:: json

                [
                  {
                    "streams": [
                      {
                        "device": 3,
                        "direction": "output",
                        "outfile": "/dev/null",
                        "infile": "/mnt/hd/media/music/audio.mp3",
                        "ffmpeg_bin": "ffmpeg",
                        "channels": 2,
                        "sample_rate": 44100,
                        "dtype": "int16",
                        "streaming": false,
                        "duration": null,
                        "blocksize": 1024,
                        "latency": "high",
                        "redis_queue": "platypush-stream-AudioResourcePlayer-3",
                        "audio_pass_through": false,
                        "state": "PAUSED",
                        "started_time": "2023-06-19T11:57:05.882329",
                        "stream_index": 1,
                        "stream_name": "platypush:audio:output:1"
                      }
                    ],
                    "index": 3,
                    "name": "default",
                    "hostapi": 0,
                    "max_input_channels": 32,
                    "max_output_channels": 32,
                    "default_samplerate": 44100,
                    "default_low_input_latency": 0.008707482993197279,
                    "default_low_output_latency": 0.008707482993197279,
                    "default_high_input_latency": 0.034829931972789115,
                    "default_high_output_latency": 0.034829931972789115
                  }
                ]

        """
        devices = self._manager.get_devices()
        streams = self._manager.get_streams()
        ret = {dev.index: {'streams': [], **asdict(dev)} for dev in devices}
        for stream in streams:
            if stream.device is None:
                continue

            dev_index = int(
                stream.device
                if isinstance(stream.device, (int, str))
                else stream.device[0]
            )

            ret[dev_index]['streams'].append(stream.asdict())

        return list(ret.values())

    @action
    def query_streams(self):
        """
        Deprecated alias for :meth:`.status`.
        """

        warnings.warn(
            'sound.query_streams is deprecated, use sound.status instead',
            DeprecationWarning,
            stacklevel=1,
        )

        return self.status()

    @action
    def stop_playback(
        self,
        device: Optional[DeviceType] = None,
        streams: Optional[Iterable[Union[int, str]]] = None,
    ):
        """
        :param device: Only stop the streams on the specified device, by name or index (default: all).
        :param streams: Streams to stop by index or name (default: all).
        """
        self._manager.stop_audio(device=device, streams=streams, type=StreamType.OUTPUT)

    @action
    def pause_playback(
        self,
        device: Optional[DeviceType] = None,
        streams: Optional[Iterable[Union[int, str]]] = None,
    ):
        """
        :param device: Only stop the streams on the specified device, by name or index (default: all).
        :param streams: Streams to stop by index or name (default: all).
        """
        self._manager.pause_audio(
            device=device, streams=streams, type=StreamType.OUTPUT
        )

    @action
    def stop_recording(
        self, device: Optional[DeviceType] = None, timeout: Optional[float] = 2
    ):
        """
        Stop the current recording process on the selected device (default:
        default input device), if it is running.
        """
        self._manager.stop_audio(device, StreamType.INPUT, timeout=timeout)

    @action
    def pause_recording(self, device: Optional[DeviceType] = None):
        """
        Toggle the recording pause state on the selected device (default:
        default input device), if it is running.

        If paused, the recording will be resumed. If running, it will be
        paused. Otherwise, no action will be taken.
        """
        self._manager.pause_audio(device, StreamType.INPUT)

    @action
    def set_volume(
        self,
        volume: float,
        device: Optional[DeviceType] = None,
        streams: Optional[Iterable[Union[int, str]]] = None,
    ):
        """
        Set the audio input/output volume.

        :param volume: New volume, between 0 and 100.
        :param device: Set the volume only on the specified device (default:
            all).
        :param streams: Set the volume only on the specified list of stream
            indices/names (default: all).
        """
        self._manager.set_volume(volume=volume, device=device, streams=streams)

    @override
    def main(self):
        try:
            self.wait_stop()
        finally:
            self._manager.stop_audio()


# vim:sw=4:ts=4:et:
