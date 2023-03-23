from collections import defaultdict
from enum import Enum
from functools import wraps
import re
from typing import Callable, Dict
from uuid import UUID

import bluetooth_numbers
from bleak.uuids import uuid16_dict, uuid128_dict

from platypush.plugins.bluetooth._types import RawServiceClass


def memoized_names(f: Callable[[str], str]):
    """
    Decorator that keeps track of the assigned names to make sure that we don't
    end up with conflicts when assigning service class enum names.
    """
    assigned_names: Dict[str, int] = defaultdict(lambda: 0)

    @wraps(f)
    def wrapper(name: str) -> str:
        name = f(name)
        assigned_names[name] += 1
        transformed_name = (
            f'{name}_{assigned_names[name]}' if assigned_names[name] > 1 else name
        )

        return transformed_name

    return wrapper


@memoized_names
def _service_name_to_enum_name(service_name: str) -> str:
    """
    Convert a service name to an enum-key compatible string.
    """
    ret = service_name.title()
    ret = re.sub(r"\(.+?\)", "", ret)
    ret = re.sub(r"\s+", "_", ret)
    ret = re.sub(r"[^a-zA-Z0-9_]", "", ret)
    ret = re.sub(r"_+", "_", ret)
    return ret.upper()


_service_classes: Dict[RawServiceClass, str] = {
    0x0: "Unknown",
    0x1000: "Service Discovery Server Service Class ID",
    0x1001: "Browse Group Descriptor Service Class ID",
    0x1101: "Serial Port",
    0x1102: "LAN Access Using PPP",
    0x1103: "Dialup Networking",
    0x1104: "IR MC Sync",
    0x1105: "OBEX Object Push",
    0x1106: "OBEX File Transfer",
    0x1107: "IR MC Sync Command",
    0x1108: "Headset",
    0x1109: "Cordless Telephony",
    0x110A: "Audio Source",
    0x110B: "Audio Sink",
    0x110C: "A/V Remote Control Target",
    0x110D: "Advanced Audio Distribution",
    0x110E: "A/V Remote Control",
    0x110F: "A/V Remote Control Controller",
    0x1110: "Intercom",
    0x1111: "Fax",
    0x1112: "Headset Audio Gateway",
    0x1113: "WAP",
    0x1114: "WAP Client",
    0x1115: "PANU",
    0x1116: "NAP",
    0x1117: "GN",
    0x1118: "Direct Printing",
    0x1119: "Reference Printing",
    0x111A: "Basic Imaging Profile",
    0x111B: "Imaging Responder",
    0x111C: "Imaging Automatic Archive",
    0x111D: "Imaging Referenced Objects",
    0x111E: "Handsfree",
    0x111F: "Handsfree Audio Gateway",
    0x1120: "Direct Printing Reference Objects Service",
    0x1121: "Reflected UI",
    0x1122: "Basic Printing",
    0x1123: "Printing Status",
    0x1124: "Human Interface Device Service",
    0x1125: "Hard Copy Cable Replacement",
    0x1126: "HCR Print",
    0x1127: "HCR Scan",
    0x1128: "Common ISDN Access",
    0x112D: "SIM Access",
    0x112E: "Phone Book Access PCE",
    0x112F: "Phone Book Access PSE",
    0x1130: "Phone Book Access",
    0x1131: "Headset NS",
    0x1132: "Message Access Server",
    0x1133: "Message Notification Server",
    0x1134: "Message Notification Profile",
    0x1135: "GNSS",
    0x1136: "GNSS Server",
    0x1137: "3D Display",
    0x1138: "3D Glasses",
    0x1139: "3D Synchronization",
    0x113A: "MPS Profile",
    0x113B: "MPS SC",
    0x113C: "CTN Access Service",
    0x113D: "CTN Notification Service",
    0x113E: "CTN Profile",
    0x1200: "PnP Information",
    0x1201: "Generic Networking",
    0x1202: "Generic File Transfer",
    0x1203: "Generic Audio",
    0x1204: "Generic Telephony",
    0x1205: "UPNP Service",
    0x1206: "UPNP IP Service",
    0x1300: "ESDP UPNP IP PAN",
    0x1301: "ESDP UPNP IP LAP",
    0x1302: "ESDP UPNP L2CAP",
    0x1303: "Video Source",
    0x1304: "Video Sink",
    0x1305: "Video Distribution",
    0x1400: "HDP",
    0x1401: "HDP Source",
    0x1402: "HDP Sink",
}
"""
Directory of known Bluetooth service UUIDs.

See
https://btprodspecificationrefs.blob.core.windows.net/assigned-numbers/Assigned%20Number%20Types/Assigned%20Numbers.pdf,
Section 3.3.
"""

_custom_service_classes: Dict[RawServiceClass, str] = {
    UUID("cba20d00-224d-11e6-9fb8-0002a5d5c51b"): "Switchbot",
}

# Update the base services with the GATT service UUIDs defined in ``bluetooth_numbers``. See
# https://btprodspecificationrefs.blob.core.windows.net/assigned-numbers/Assigned%20Number%20Types/Assigned%20Numbers.pdf,
# Section 3.4
_service_classes.update(bluetooth_numbers.service)

# Extend the service classes with the GATT service UUIDs defined in Bleak
_service_classes.update(_custom_service_classes)
_service_classes.update({UUID(uuid): name for uuid, name in uuid128_dict.items()})
_service_classes.update(uuid16_dict)  # type: ignore

_service_classes_by_name: Dict[str, RawServiceClass] = {
    name: cls for cls, name in _service_classes.items()
}


class _ServiceClassMeta:
    """
    Metaclass for :class:`ServiceClass`.
    """

    value: RawServiceClass
    """ The raw service class value. """

    @classmethod
    def get(cls, value: RawServiceClass) -> "ServiceClass":
        """
        :param value: The raw service class UUID.
        :return: The parsed :class:`ServiceClass` instance, or
            ``ServiceClass.UNKNOWN``.
        """
        try:
            return ServiceClass(value)
        except ValueError:
            try:
                if isinstance(value, UUID):
                    return ServiceClass(int(str(value).upper()[4:8], 16))
            except ValueError:
                pass

            return ServiceClass.UNKNOWN  # type: ignore

    @classmethod
    def by_name(cls, name: str) -> "ServiceClass":
        """
        :param name: The name of the service class.
        :return: The :class:`ServiceClass` instance, or
            ``ServiceClass.UNKNOWN``.
        """
        return (
            ServiceClass(_service_classes_by_name.get(name))
            or ServiceClass.UNKNOWN  # type: ignore
        )

    def __str__(self) -> str:
        return _service_classes.get(
            self.value, ServiceClass.UNKNOWN.value  # type: ignore
        )

    def __repr__(self) -> str:
        return f"<{self.value}: {str(self)}>"


ServiceClass = Enum(  # type: ignore
    "ServiceClass",
    {_service_name_to_enum_name(name): cls for cls, name in _service_classes.items()},
    type=_ServiceClassMeta,
)
""" Enumeration of known Bluetooth services. """
