import subprocess
from functools import lru_cache
import re
from typing import Dict, List, Optional, Set, Union

import sounddevice as sd


AudioDeviceName = Optional[Union[int, str]]

_IGNORED_DEVICE_TOKENS = {
    'alsa',
    'audio',
    'device',
    'fallback',
    'hifi',
    'input',
    'mono',
    'output',
    'pci',
    'sink',
    'source',
    'usb',
}


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

    return (
        _pulse_device_descriptions(kind).get(device)
        or _resolve_device_by_tokens(device, kind)
        or device
    )


def _resolve_device_by_tokens(device: str, kind: str) -> Optional[str]:
    """
    Resolve a PulseAudio/PipeWire device name without using ``pactl``.

    This is a best-effort fallback for minimal containers where ``pactl`` is
    unavailable or cannot connect to the Pulse server. It matches stable Pulse
    names like ``alsa_input.usb-CMEDIA_USB_PnP_Audio_Device-00.mono-fallback``
    against the device names exposed by PortAudio/sounddevice.
    """
    source_tokens = _tokenize_device_name(device)
    if not source_tokens:
        return None

    candidates = []
    for candidate in _sounddevice_names(kind):
        candidate_tokens = _tokenize_device_name(candidate)
        if not candidate_tokens:
            continue

        overlap = source_tokens & candidate_tokens
        score = len(overlap)
        if not score:
            continue

        # Prefer candidates that match a larger fraction of their own
        # significant tokens, so "USB PnP Audio Device Mono" wins over generic
        # devices that happen to share only "usb".
        ratio = score / len(candidate_tokens)
        candidates.append((score, ratio, candidate))

    if not candidates:
        return None

    candidates.sort(key=lambda item: (item[0], item[1]), reverse=True)
    return candidates[0][2]


def _sounddevice_names(kind: str) -> List[str]:
    devices: List[dict] = sd.query_devices()  # type: ignore
    channel_key = f'max_{kind}_channels'
    return [
        dev['name']
        for dev in devices
        if dev.get(channel_key, 0) and isinstance(dev.get('name'), str)
    ]


def _tokenize_device_name(device: str) -> Set[str]:
    normalized = re.sub(r'(?<!\d)([A-Za-z]+)(\d+)', r'\1 \2', device).lower()
    tokens = {
        token
        for token in re.split(r'[^a-z0-9]+', normalized)
        if (
            token
            and token not in _IGNORED_DEVICE_TOKENS
            and set(token) != {'0'}
            and (len(token) > 1 or token.isdigit())
        )
    }

    return tokens
