from sqlalchemy import Column, Integer, Boolean, ForeignKey

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

        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }
