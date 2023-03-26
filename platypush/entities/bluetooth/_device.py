from typing import Iterable, List
from typing_extensions import override

from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    JSON,
    String,
)

from platypush.common.db import Base

from ..devices import Device
from ._service import BluetoothService


if 'bluetooth_device' not in Base.metadata:

    class BluetoothDevice(Device):
        """
        Entity that represents a Bluetooth device.
        """

        __tablename__ = 'bluetooth_device'

        id = Column(
            Integer, ForeignKey(Device.id, ondelete='CASCADE'), primary_key=True
        )

        address = Column(String, nullable=False)
        """ Device address. """

        connected = Column(Boolean, default=False)
        """ Whether the device is connected. """

        supports_ble = Column(Boolean, default=False)
        """
        Whether the device supports the Bluetooth Low-Energy specification.
        """

        supports_legacy = Column(Boolean, default=False)
        """
        Whether the device supports the legacy (non-BLE) specification.
        """

        rssi = Column(Integer, default=None)
        """ Received Signal Strength Indicator. """

        tx_power = Column(Integer, default=None)
        """ Reported transmission power. """

        _major_service_classes = Column("major_service_classes", JSON, default=None)
        """ The reported major service classes, as a list of strings. """

        _major_device_class = Column("major_device_class", String, default=None)
        """ The reported major device class. """

        _minor_device_classes = Column("minor_device_classes", JSON, default=None)
        """ The reported minor device classes, as a list of strings. """

        manufacturer = Column(String, default=None)
        """ Device manufacturer, as a string. """

        model = Column(String, default=None)
        """ Device model, as a string. """

        model_id = Column(String, default=None)
        """ Device model ID. """

        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }

        @property
        def major_device_class(self):
            from platypush.plugins.bluetooth.model import MajorDeviceClass

            ret = MajorDeviceClass.UNKNOWN
            if self._major_device_class:
                matches = [
                    cls
                    for cls in MajorDeviceClass
                    if cls.value.name == self._major_device_class
                ]

                if matches:
                    ret = matches[0]

            return ret

        @major_device_class.setter
        def major_device_class(self, value):
            self._major_device_class = value.value.name

        @property
        def minor_device_classes(self) -> list:
            from platypush.plugins.bluetooth.model import MinorDeviceClass

            ret = []
            for dev_cls in self._minor_device_classes or []:
                matches = [cls for cls in MinorDeviceClass if cls.value.name == dev_cls]

                if matches:
                    ret.append(matches[0])

            return ret

        @minor_device_classes.setter
        def minor_device_classes(self, value: Iterable):
            self._minor_device_classes = [cls.value.name for cls in (value or [])]

        @property
        def major_service_classes(self) -> list:
            from platypush.plugins.bluetooth.model import MajorServiceClass

            ret = []
            for dev_cls in self._major_service_classes or []:
                matches = [
                    cls for cls in MajorServiceClass if cls.value.name == dev_cls
                ]

                if matches:
                    ret.append(matches[0])

            return ret

        @major_service_classes.setter
        def major_service_classes(self, value: Iterable):
            self._major_service_classes = [cls.value.name for cls in (value or [])]

        @property
        def services(self) -> List[BluetoothService]:
            """
            :return: List of
            :class:`platypush.plugins.bluetooth.model.BluetoothService` mapping
            all the services exposed by the device.
            """
            return [
                child for child in self.children if isinstance(child, BluetoothService)
            ]

        @property
        def known_services(self) -> dict:
            """
            Known services exposed by the device, indexed by
            :class:`platypush.plugins.bluetooth.model.ServiceClass` enum value.
            """
            from platypush.plugins.bluetooth.model import ServiceClass

            return {
                child.service_class: child
                for child in self.children
                if isinstance(child, BluetoothService)
                and child.service_class != ServiceClass.UNKNOWN
            }

        @override
        def to_dict(self):
            """
            Overwrites ``to_dict`` to transform private column names into their
            public representation.
            """
            return {k.lstrip('_'): v for k, v in super().to_dict().items()}
