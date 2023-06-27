from collections import defaultdict
from logging import getLogger
from threading import RLock
from typing import Dict, Iterable, List, Optional, Union

from .._model import AudioDevice, DeviceType, StreamType
from .._streams import AudioThread
from ._device import DeviceManager


class StreamManager:
    """
    The audio manager is responsible for storing the current state of the
    playing/recording audio streams and allowing fast flexible lookups (by
    stream index, name, type, device, and any combination of those).
    """

    def __init__(self, device_manager: DeviceManager):
        """
        :param device_manager: Reference to the device manager.
        """
        self._next_stream_index = 1
        self._device_manager = device_manager
        self._state_lock = RLock()
        self._stream_index_by_name: Dict[str, int] = {}
        self._stream_name_by_index: Dict[int, str] = {}
        self._stream_index_to_device: Dict[int, AudioDevice] = {}
        self._stream_index_to_type: Dict[int, StreamType] = {}
        self.logger = getLogger(__name__)

        self._streams: Dict[
            int, Dict[StreamType, Dict[int, AudioThread]]
        ] = defaultdict(lambda: {stream_type: {} for stream_type in StreamType})
        """ {device_index: {stream_type: {stream_index: audio_thread}}} """

        self._streams_by_index: Dict[StreamType, Dict[int, AudioThread]] = {
            stream_type: {} for stream_type in StreamType
        }
        """ {stream_type: {stream_index: [audio_threads]}} """

        self._stream_locks: Dict[int, Dict[StreamType, RLock]] = defaultdict(
            lambda: {stream_type: RLock() for stream_type in StreamType}
        )
        """ {device_index: {stream_type: RLock}} """

    @classmethod
    def _generate_stream_name(
        cls,
        type: StreamType,  # pylint: disable=redefined-builtin
        stream_index: int,
    ) -> str:
        return f'platypush:audio:{type.value}:{stream_index}'

    def _gen_next_stream_index(
        self,
        type: StreamType,  # pylint: disable=redefined-builtin
        stream_name: Optional[str] = None,
    ) -> int:
        """
        :param type: The type of the stream to allocate (input or output).
        :param stream_name: The name of the stream to allocate.
        :return: The index of the new stream.
        """
        with self._state_lock:
            stream_index = self._next_stream_index

            if not stream_name:
                stream_name = self._generate_stream_name(type, stream_index)

            self._stream_name_by_index[stream_index] = stream_name
            self._stream_index_by_name[stream_name] = stream_index
            self._next_stream_index += 1

        return stream_index

    def register(
        self,
        audio_thread: AudioThread,
        device: AudioDevice,
        type: StreamType,  # pylint: disable=redefined-builtin
        stream_name: Optional[str] = None,
    ):
        """
        Registers an audio stream to a device.

        :param audio_thread: Stream to register.
        :param device: Device to register the stream to.
        :param type: The type of the stream to allocate (input or output).
        :param stream_name: The name of the stream to allocate.
        """
        with self._state_lock:
            stream_index = audio_thread.stream_index
            if stream_index is None:
                stream_index = audio_thread.stream_index = self._gen_next_stream_index(
                    type, stream_name=stream_name
                )

            self._streams[device.index][type][stream_index] = audio_thread
            self._stream_index_to_device[stream_index] = device
            self._stream_index_to_type[stream_index] = type
            self._streams_by_index[type][stream_index] = audio_thread

    def unregister(
        self,
        audio_thread: AudioThread,
        device: Optional[AudioDevice] = None,
        type: Optional[StreamType] = None,  # pylint: disable=redefined-builtin
    ):
        """
        Unregisters an audio stream from a device.

        :param audio_thread: Stream to unregister.
        :param device: Device to unregister the stream from.
        :param type: The type of the stream to unregister (input or output).
        """
        with self._state_lock:
            stream_index = audio_thread.stream_index
            if stream_index is None:
                return

            if device is None:
                device = self._stream_index_to_device.get(stream_index)

            if not type:
                type = self._stream_index_to_type.get(stream_index)

            if device is None or type is None:
                return

            self._streams[device.index][type].pop(stream_index, None)
            self._stream_index_to_device.pop(stream_index, None)
            self._stream_index_to_type.pop(stream_index, None)
            self._streams_by_index[type].pop(stream_index, None)
            stream_name = self._stream_name_by_index.pop(stream_index, None)
            if stream_name:
                self._stream_index_by_name.pop(stream_name, None)

    def _get_by_device_and_type(
        self,
        device: Optional[DeviceType] = None,
        type: Optional[StreamType] = None,  # pylint: disable=redefined-builtin
    ) -> List[AudioThread]:
        """
        Filter streams by device and/or type.
        """
        devs = (
            [self._device_manager.get_device(device, type)]
            if device is not None
            else self._device_manager.get_devices(type)
        )

        return [
            audio_thread
            for dev in devs
            for stream_info in (
                [self._streams[dev.index].get(type, {})]
                if type
                else list(self._streams[dev.index].values())
            )
            for audio_thread in stream_info.values()
            if audio_thread and audio_thread.is_alive()
        ]

    def _get_by_stream_index_or_name(
        self, streams: Iterable[Union[str, int]]
    ) -> List[AudioThread]:
        """
        Filter streams by index or name.
        """
        threads = []

        for stream in streams:
            try:
                stream_index = int(stream)
            except (TypeError, ValueError):
                stream_index = self._stream_index_by_name.get(stream)  # type: ignore
                if stream_index is None:
                    self.logger.warning('No such audio stream: %s', stream)
                    continue

            stream_type = self._stream_index_to_type.get(stream_index)
            if not stream_type:
                self.logger.warning(
                    'No type available for this audio stream: %s', stream
                )
                continue

            thread = self._streams_by_index.get(stream_type, {}).get(stream_index)
            if thread:
                threads.append(thread)

        return threads

    def get(
        self,
        device: Optional[DeviceType] = None,
        type: Optional[StreamType] = None,  # pylint: disable=redefined-builtin
        streams: Optional[Iterable[Union[str, int]]] = None,
    ) -> List[AudioThread]:
        """
        Searches streams, either by device and/or type, or by stream index/name.
        """
        return (
            self._get_by_stream_index_or_name(streams)
            if streams
            else self._get_by_device_and_type(device, type)
        )
