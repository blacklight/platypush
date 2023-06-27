from typing import List, Optional

import sounddevice as sd

from .._model import AudioDevice, DeviceType, StreamType


class DeviceManager:
    """
    The device manager is responsible for managing the virtual audio device
    abstractions exposed by the OS.

    For example, on a pure ALSA system virtual devices are usually mapped the
    physical audio devices available on the system.

    On a system that runs through PulseAudio or Jack, there may be a
    ``default`` virtual device whose sound card mappings may be managed by the
    audio server.
    """

    def __init__(
        self,
        input_device: Optional[DeviceType] = None,
        output_device: Optional[DeviceType] = None,
    ):
        """
        :param input_device: The default input device to use (by index or name).
        :param output_device: The default output device to use (by index or name).
        """
        self.input_device = (
            self.get_device(input_device, StreamType.INPUT)
            if input_device is not None
            else None
        )

        self.output_device = (
            self.get_device(output_device, StreamType.OUTPUT)
            if output_device is not None
            else None
        )

    def get_devices(
        self, type: Optional[StreamType] = None  # pylint: disable=redefined-builtin
    ) -> List[AudioDevice]:
        """
        Get available audio devices.

        :param type: The type of devices to filter (default: return all).
        """
        devices: List[dict] = sd.query_devices()  # type: ignore
        if type:
            devices = [dev for dev in devices if dev.get(f'max_{type.value}_channels')]

        return [AudioDevice(**info) for info in devices]

    def get_device(
        self,
        device: Optional[DeviceType] = None,
        type: Optional[StreamType] = None,  # pylint: disable=redefined-builtin
    ) -> AudioDevice:
        """
        Search for a device.

        Either ``device`` or ``type`` have to be specified.

        :param device: The device to search for, either by index or name. If
            not specified, then the default device for the given type is
            returned.
        :param type: The type of the device to search.
        """
        assert device or type, 'Please specify either device or type'
        if device is None:
            if type == StreamType.INPUT and self.input_device is not None:
                return self.input_device
            if type == StreamType.OUTPUT and self.output_device is not None:
                return self.output_device

        try:
            info: dict = sd.query_devices(
                kind=type.value if type else None, device=device  # type: ignore
            )
        except sd.PortAudioError as e:
            raise AssertionError(
                f'Could not get device for type={type} and device={device}: {e}',
                type,
                device,
                e,
            ) from e

        assert info, f'No such device: {device}'
        return AudioDevice(**info)
