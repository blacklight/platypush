from ._base import BaseBluetoothClass, ClassProperty


class MajorServiceClass(BaseBluetoothClass):
    """
    Models Bluetooth major service classes - see
    https://btprodspecificationrefs.blob.core.windows.net/assigned-numbers/Assigned%20Number%20Types/Assigned%20Numbers.pdf,
    Section 2.8.1
    """

    LE_AUDIO = ClassProperty('Low-energy Audio', 1 << 14, 14)
    POSITIONING = ClassProperty('Positioning', 1 << 16, 16)
    NETWORKING = ClassProperty('Networking', 1 << 17, 17)
    RENDERING = ClassProperty('Rendering', 1 << 18, 18)
    CAPTURING = ClassProperty('Capturing', 1 << 19, 19)
    OBJECT_TRANSFER = ClassProperty('Object Transfer', 1 << 20, 20)
    AUDIO = ClassProperty('Audio', 1 << 21, 21)
    TELEPHONY = ClassProperty('Telephony', 1 << 22, 22)
    INFORMATION = ClassProperty('Information', 1 << 23, 23)
