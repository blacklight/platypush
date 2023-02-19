from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    JSON,
    String,
)

from platypush.common.db import Base

from .devices import Device


if 'bluetooth_device' not in Base.metadata:

    class BluetoothDevice(Device):
        """
        Entity that represents a Bluetooth device.
        """

        __tablename__ = 'bluetooth_device'

        id = Column(
            Integer, ForeignKey(Device.id, ondelete='CASCADE'), primary_key=True
        )

        connected = Column(Boolean, default=False)
        """ Whether the device is connected. """

        paired = Column(Boolean, default=False)
        """ Whether the device is paired. """

        trusted = Column(Boolean, default=False)
        """ Whether the device is trusted. """

        blocked = Column(Boolean, default=False)
        """ Whether the device is blocked. """

        rssi = Column(Integer, default=None)
        """ Received Signal Strength Indicator. """

        tx_power = Column(Integer, default=None)
        """ Reported transmission power. """

        manufacturers = Column(JSON)
        """ Registered manufacturers for the device, as an ID -> Name map. """

        uuids = Column(JSON)
        """
        Service/characteristic UUIDs exposed by the device, as a
        UUID -> Name map.
        """

        brand = Column(String)
        """ Device brand, as a string. """

        model = Column(String)
        """ Device model, as a string. """

        model_id = Column(String)
        """ Device model ID. """

        manufacturer_data = Column(JSON)
        """
        Latest manufacturer data published by the device, as a
        ``manufacturer_id -> data`` map, where ``data`` is a hexadecimal
        string.
        """

        service_data = Column(JSON)
        """
        Latest service data published by the device, as a ``service_uuid ->
        data`` map, where ``data`` is a hexadecimal string.
        """

        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }
