from logging import getLogger
import os
import stat
from threading import Event
from time import time
from typing import Iterable, List, Optional, Union

from .._model import AudioDevice, DeviceType, StreamType
from .._streams import AudioPlayer, AudioRecorder, AudioThread
from ._device import DeviceManager
from ._stream import StreamManager


class AudioManager:
    """
    The audio manager is responsible for managing multiple audio controllers and
    their access to audio resources.

    It main purpose is to act as a proxy/facade between the high-level audio
    plugin and the audio functionalities (allocating streams, managing the state
    of the player and recorder processes, etc.).
    """

    _default_signal_timeout = 2

    def __init__(
        self,
        should_stop: Event,
        input_blocksize: int,
        output_blocksize: int,
        input_device: Optional[DeviceType] = None,
        output_device: Optional[DeviceType] = None,
        queue_size: Optional[int] = None,
    ):
        """
        :param should_stop: Event to synchronize the audio manager stop.
        :param input_blocksize: Block size for the input stream.
        :param output_blocksize: Block size for the output stream.
        :param input_device: Default device to use for the input stream.
        :param output_device: Default device to use for the output stream.
        :param queue_size: Maximum size of the audio queues.
        """
        self._should_stop = should_stop
        self._device_manager = DeviceManager(
            input_device=input_device, output_device=output_device
        )

        self._stream_manager = StreamManager(device_manager=self._device_manager)
        self.logger = getLogger(__name__)
        self.input_blocksize = input_blocksize
        self.output_blocksize = output_blocksize
        self.queue_size = queue_size

    def create_player(
        self,
        device: DeviceType,
        channels: int,
        volume: float,
        infile: Optional[str] = None,
        sound: Optional[Union[dict, Iterable[dict]]] = None,
        duration: Optional[float] = None,
        sample_rate: Optional[int] = None,
        dtype: str = 'int16',
        blocksize: Optional[int] = None,
        latency: Union[float, str] = 'high',
        stream_name: Optional[str] = None,
    ) -> AudioPlayer:
        """
        Create an audio player thread.

        :param device: Audio device to use.
        :param channels: Number of output channels.
        :param volume: Output volume, between 0 and 100.
        :param infile: File or URL to play.
        :param sound: Alternatively to a file/URL, you can play synthetic
            sounds.
        :param duration: Duration of the stream in seconds.
        :param sample_rate: Sample rate of the stream.
        :param dtype: Data type of the stream.
        :param blocksize: Block size of the stream.
        :param latency: Latency of the stream.
        :param stream_name: Name of the stream.
        """
        dev = self._device_manager.get_device(device, type=StreamType.OUTPUT)
        player = AudioPlayer.build(
            device=device,
            infile=infile,
            sound=sound,
            duration=duration,
            volume=volume,
            sample_rate=sample_rate or dev.default_samplerate,
            dtype=dtype,
            blocksize=blocksize or self.output_blocksize,
            latency=latency,
            channels=channels,
            queue_size=self.queue_size,
            should_stop=self._should_stop,
        )

        self._stream_manager.register(
            player, dev, StreamType.OUTPUT, stream_name=stream_name
        )
        return player

    def create_recorder(
        self,
        device: DeviceType,
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
    ) -> AudioRecorder:
        """
        Create an audio recorder thread.

        :param device: Audio device to use.
        :param output_device: Output device to use.
        :param fifo: Path to an output FIFO file to use to synchronize the audio
            to other processes.
        :param outfile: Optional output file for the recorded audio.
        :param duration: Duration of the recording in seconds.
        :param sample_rate: Sample rate of the stream.
        :param dtype: Data type of the stream.
        :param blocksize: Block size of the stream.
        :param latency: Latency of the stream.
        :param channels: Number of output channels.
        :param volume: Input volume, between 0 and 100.
        :param redis_queue: Name of the Redis queue to use.
        :param format: Format of the recorded audio.
        :param stream: Whether to stream the recorded audio.
        :param play_audio: Whether to play the recorded audio in real-time.
        :param stream_name: Name of the stream.
        """
        blocksize = blocksize or self.input_blocksize
        dev = self._device_manager.get_device(device, type=StreamType.OUTPUT)

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
        recorder = AudioRecorder(
            device=(
                (
                    dev.index,
                    self._device_manager.get_device(
                        type=StreamType.OUTPUT, device=output_device
                    ).index,
                )
                if play_audio
                else dev.index
            ),
            outfile=outfile,
            duration=duration,
            sample_rate=sample_rate or dev.default_samplerate,
            dtype=dtype,
            blocksize=blocksize,
            latency=latency,
            output_format=format,
            channels=channels,
            volume=volume,
            redis_queue=redis_queue,
            stream=stream,
            audio_pass_through=play_audio,
            queue_size=self.queue_size,
            should_stop=self._should_stop,
        )

        self._stream_manager.register(
            recorder, dev, StreamType.INPUT, stream_name=stream_name
        )
        return recorder

    def get_device(
        self,
        device: Optional[DeviceType] = None,
        type: Optional[StreamType] = None,  # pylint: disable=redefined-builtin
    ) -> AudioDevice:
        """
        Proxy to ``self._device_manager.get_device``.
        """
        return self._device_manager.get_device(device=device, type=type)

    def get_devices(
        self,
        type: Optional[StreamType] = None,  # pylint: disable=redefined-builtin
    ) -> List[AudioDevice]:
        """
        Proxy to ``self._device_manager.get_devices``.
        """
        return self._device_manager.get_devices(type=type)

    def get_streams(
        self,
        device: Optional[DeviceType] = None,
        type: Optional[StreamType] = None,  # pylint: disable=redefined-builtin
        streams: Optional[Iterable[Union[str, int]]] = None,
    ) -> List[AudioThread]:
        """
        Proxy to ``self._stream_manager.get``.
        """
        return self._stream_manager.get(device=device, type=type, streams=streams)

    def stop_audio(
        self,
        device: Optional[DeviceType] = None,
        type: Optional[StreamType] = None,  # pylint: disable=redefined-builtin
        streams: Optional[Iterable[Union[str, int]]] = None,
        timeout: Optional[float] = 2,
    ):
        """
        Stops audio sessions.

        :param device: Filter by host audio device.
        :param type: Filter by stream type (input or output).
        :param streams: Filter by stream indices/names.
        :param timeout: Wait timeout in seconds.
        """
        streams_to_stop = self._stream_manager.get(device, type, streams=streams)

        # Send the stop signals
        for audio_thread in streams_to_stop:
            audio_thread.notify_stop()

        # Wait for termination (with timeout)
        wait_start = time()
        for audio_thread in streams_to_stop:
            audio_thread.join(
                timeout=max(0, timeout - (time() - wait_start))
                if timeout is not None
                else None
            )

        # Remove references
        for audio_thread in streams_to_stop:
            self._stream_manager.unregister(audio_thread)

    def pause_audio(
        self,
        device: Optional[DeviceType] = None,
        type: Optional[StreamType] = None,  # pylint: disable=redefined-builtin
        streams: Optional[Iterable[Union[str, int]]] = None,
    ):
        """
        Pauses/resumes audio sessions.

        :param device: Filter by host audio device.
        :param type: Filter by stream type (input or output).
        :param streams: Filter by stream indices/names.
        """
        streams_to_pause = self._stream_manager.get(device, type, streams=streams)

        # Send the pause toggle signals
        for audio_thread in streams_to_pause:
            audio_thread.notify_pause()

    def set_volume(
        self,
        volume: float,
        device: Optional[DeviceType] = None,
        streams: Optional[Iterable[Union[str, int]]] = None,
    ):
        """
        :param volume: New volume, between 0 and 100.
        :param device: Set the volume only on the specified device (default:
            all).
        :param streams: Set the volume only on the specified list of stream
            indices/names (default: all).
        """
        stream_objs = self._stream_manager.get(device=device, streams=streams)

        for stream in stream_objs:
            stream.volume = volume
