DEFAULT_APP_ID = 'CC1AD845'
DEFAULT_DISPLAY_NAME = 'Default Media Receiver'
DEFAULT_MANUFACTURER = 'Platypush'
DEFAULT_MODEL_NAME = 'Platypush'
DEFAULT_DEVICE_NAME = 'Platypush'

NAMESPACE_CONNECTION = 'urn:x-cast:com.google.cast.tp.connection'
NAMESPACE_DEVICEAUTH = 'urn:x-cast:com.google.cast.tp.deviceauth'
NAMESPACE_HEARTBEAT = 'urn:x-cast:com.google.cast.tp.heartbeat'
NAMESPACE_RECEIVER = 'urn:x-cast:com.google.cast.receiver'
NAMESPACE_MEDIA = 'urn:x-cast:com.google.cast.media'

DEFAULT_PORT: int = 8009
DEFAULT_STATUS_INTERVAL: float = 1.0
DEFAULT_CAPABILITIES_AV: int = 5
DEFAULT_CAPABILITIES_AUDIO: int = 4

SUPPORTED_MEDIA_COMMANDS: int = 12303

RECEIVER_STATUS_IDLE = 'Ready To Cast'
RECEIVER_STATUS_PLAYING = 'Playing'
RECEIVER_STATUS_PAUSED = 'Paused'

STREAM_TYPE_BUFFERED = 'BUFFERED'
STREAM_TYPE_LIVE = 'LIVE'
STREAM_TYPE_NONE = 'NONE'

PRIVATE_NETWORKS = [
    '192.168.0.0/16',
    '10.0.0.0/8',
    '172.16.0.0/12',
]

# ---------------------------------------------------------------------------
# DIAL / SSDP
# ---------------------------------------------------------------------------

DIAL_SSDP_MCAST_ADDR: str = '239.255.255.250'
DIAL_SSDP_PORT: int = 1900
DIAL_ST_DIAL: str = 'urn:dial-multiscreen-org:service:dial:1'
DIAL_ST_ALL: str = 'ssdp:all'
DIAL_ST_ROOTDEVICE: str = 'upnp:rootdevice'
DIAL_ELIGIBLE_ST: frozenset = frozenset(
    s.lower() for s in {DIAL_ST_DIAL, DIAL_ST_ALL, DIAL_ST_ROOTDEVICE}
)
DIAL_SSDP_MX_MAX: int = 5
DIAL_SSDP_RECV_BUF: int = 4096
DIAL_LAUNCH_TIMEOUT: float = 5.0  # seconds; Flask route waits this long for bus reply
