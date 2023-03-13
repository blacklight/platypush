from typing import Iterable, List, Optional

from bluetooth_numbers import oui

from platypush.entities.bluetooth import BluetoothDevice, BluetoothService

from platypush.plugins.bluetooth.model import (
    MajorServiceClass,
    MajorDeviceClass,
    MinorDeviceClass,
)


# pylint: disable=too-few-public-methods
class BluetoothDeviceBuilder:
    """
    :class:`platypush.entity.bluetooth.BluetoothDevice` entity builder from the
    raw pybluez data.
    """

    @classmethod
    def build(
        cls,
        address: str,
        name: str,
        raw_class: int,
        services: Optional[Iterable[BluetoothService]] = None,
    ) -> BluetoothDevice:
        """
        Builds a :class:`platypush.entity.bluetooth.BluetoothDevice` from the
        raw pybluez data.
        """
        return BluetoothDevice(
            id=address,
            address=address,
            name=name,
            major_service_classes=cls._parse_major_service_classes(raw_class),
            major_device_class=cls._parse_major_device_class(raw_class),
            minor_device_classes=cls._parse_minor_device_classes(raw_class),
            manufacturer=cls._parse_manufacturer(address),
            supports_legacy=True,
            supports_ble=False,
            children=services,
        )

    @staticmethod
    def _parse_major_device_class(raw_class: int) -> MajorDeviceClass:
        """
        Parse the device major class from the raw exposed class value.
        """
        device_classes = [
            cls for cls in MajorDeviceClass if cls.value.matches(raw_class)
        ]

        return device_classes[0] if device_classes else MajorDeviceClass.UNKNOWN

    @staticmethod
    def _parse_minor_device_classes(raw_class: int) -> List[MinorDeviceClass]:
        """
        Parse the device minor classes from the raw exposed class value.
        """
        return [cls for cls in MinorDeviceClass if cls.value.matches(raw_class)]

    @staticmethod
    def _parse_major_service_classes(raw_class: int) -> List[MajorServiceClass]:
        """
        Parse the device major service classes from the raw exposed class value.
        """
        return [cls for cls in MajorServiceClass if cls.value.matches(raw_class)]

    @staticmethod
    def _parse_manufacturer(address: str) -> Optional[str]:
        """
        Parse the device manufacturer name from the raw MAC address.
        """
        return oui.get(':'.join(address.split(':')[:3]).upper())
