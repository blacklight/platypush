from .._base import BaseBluetoothClass, ClassProperty


class MajorDeviceClass(BaseBluetoothClass):
    """
    Models Bluetooth major device classes - see
    https://btprodspecificationrefs.blob.core.windows.net/assigned-numbers/Assigned%20Number%20Types/Assigned%20Numbers.pdf,
    Section 2.8.2
    """

    UNKNOWN = ClassProperty('Unknown', 0x1F00, 8, 0b0000)
    COMPUTER = ClassProperty('Computer', 0x1F00, 8, 0b0001)
    PHONE = ClassProperty('Phone', 0x1F00, 8, 0b0010)
    AP = ClassProperty('LAN / Network Access Point', 0x1F00, 8, 0b0011)
    MULTIMEDIA = ClassProperty('Audio / Video', 0x1F00, 8, 0b0100)
    PERIPHERAL = ClassProperty('Peripheral', 0x1F00, 8, 0b0101)
    IMAGING = ClassProperty('Imaging', 0x1F00, 8, 0b0110)
    WEARABLE = ClassProperty('Wearable', 0x1F00, 8, 0b0111)
    TOY = ClassProperty('Toy', 0x1F00, 8, 0b1000)
    HEALTH = ClassProperty('Health', 0x1F00, 8, 0b1001)
