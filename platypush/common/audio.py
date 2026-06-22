import subprocess
from functools import lru_cache
from typing import Dict, Optional, Union


AudioDeviceName = Optional[Union[int, str]]


@lru_cache(maxsize=2)
def _pulse_device_descriptions(kind: str) -> Dict[str, str]:
    """
    Map PulseAudio/PipeWire device names to their user-facing descriptions.

    PortAudio/sounddevice usually exposes Pulse/PipeWire devices by their
    descriptions, while Pulse uses stable names such as
    ``alsa_input.usb-...``. This helper lets callers accept either form.
    """
    pactl_type = 'sources' if kind == 'input' else 'sinks'

    try:
        proc = subprocess.run(
            ['pactl', 'list', pactl_type],
            capture_output=True,
            text=True,
            timeout=2,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return {}

    if proc.returncode != 0:
        return {}

    devices: Dict[str, str] = {}
    name = description = None

    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line:
            continue

        if line.startswith(('Source #', 'Sink #')):
            if name and description:
                devices[name] = description
            name = description = None
            continue

        if line.startswith('Name:'):
            name = line.split(':', 1)[1].strip()
        elif line.startswith('Description:'):
            description = line.split(':', 1)[1].strip()

    if name and description:
        devices[name] = description

    return devices


def resolve_audio_device(device: AudioDeviceName, kind: str) -> AudioDeviceName:
    """
    Resolve PulseAudio/PipeWire stable device names to sounddevice names.

    :param device: Device index/name, or None.
    :param kind: Either ``input`` or ``output``.
    """
    if not isinstance(device, str):
        return device

    return _pulse_device_descriptions(kind).get(device, device)
