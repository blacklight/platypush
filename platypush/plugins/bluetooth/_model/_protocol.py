from enum import Enum


class Protocol(Enum):
    """
    Models a Bluetooth protocol.
    """

    UNKNOWN = 'UNKNOWN'
    RFCOMM = 'RFCOMM'
    L2CAP = 'L2CAP'
    TCP = 'TCP'
    UDP = 'UDP'
    SDP = 'SDP'
    BNEP = 'BNEP'
    TCS_BIN = 'TCS-BIN'
    TCS_AT = 'TCS-AT'
    OBEX = 'OBEX'
    IP = 'IP'
    FTP = 'FTP'
    HTTP = 'HTTP'
    WSP = 'WSP'
    UPNP = 'UPNP'
    HIDP = 'HIDP'
    AVCTP = 'AVCTP'
    AVDTP = 'AVDTP'
    CMTP = 'CMTP'
    UDI_C_PLANE = 'UDI_C-Plane'
    HardCopyControlChannel = 'HardCopyControlChannel'
    HardCopyDataChannel = 'HardCopyDataChannel'
    HardCopyNotification = 'HardCopyNotification'

    def __str__(self) -> str:
        """
        Only returns the value of the enum.
        """
        return self.value

    def __repr__(self) -> str:
        """
        Only returns the value of the enum.
        """
        return str(self)
