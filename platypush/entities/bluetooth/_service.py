from uuid import UUID

from typing_extensions import override

from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
)

from platypush.common.db import Base
from platypush.entities import Entity

if 'bluetooth_service' not in Base.metadata:

    class BluetoothService(Entity):
        """
        Entity that represents a Bluetooth service.
        """

        __tablename__ = 'bluetooth_service'

        id = Column(
            Integer, ForeignKey(Entity.id, ondelete='CASCADE'), primary_key=True
        )

        _uuid = Column('uuid', String, nullable=False)
        """
        The service class UUID. It can be either a 16-bit or a 128-bit UUID.
        """

        _protocol = Column('protocol', String, default=None)
        """ The protocol used by the service. """

        port = Column(Integer, default=None)
        """ The port used by the service. """

        version = Column(Integer, default=None)
        """ The version of the service profile. """

        is_ble = Column(Boolean, default=False)
        """ Whether the service is a BLE service. """

        connected = Column(Boolean, default=False)
        """ Whether an active connection exists to this service. """

        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }

        @staticmethod
        def to_uuid(value):
            """
            Convert a raw UUID string to a service class UUID.
            """
            # If it's already a UUID or an int, just return it.
            if isinstance(value, (UUID, int)):
                return value
            try:
                # If it's formatted like a 128-bit UUID, convert it to a UUID
                # object.
                return UUID(value)
            except ValueError:
                # Hex string case
                return int(value, 16)

        @property
        def uuid(self):
            """
            Getter for the service class UUID.
            """
            return self.to_uuid(self._uuid)

        @uuid.setter
        def uuid(self, value):
            """
            Setter for the service class UUID.
            """
            uuid = self.to_uuid(value)
            if isinstance(uuid, int):
                # Hex-encoded 16-bit UUID case
                uuid = f'{uuid:04X}'

            self._uuid = str(uuid)

        @property
        def protocol(self):
            """
            Getter for the protocol used by the service.
            """
            from platypush.plugins.bluetooth.model import Protocol

            try:
                return Protocol(self._protocol)
            except ValueError:
                return Protocol.UNKNOWN

        @protocol.setter
        def protocol(self, value):
            """
            Setter for the protocol used by the service.
            """
            from platypush.plugins.bluetooth.model import Protocol

            protocol = Protocol.UNKNOWN
            if isinstance(value, Protocol):
                protocol = value
            else:
                try:
                    protocol = Protocol(value)
                except ValueError:
                    pass

            self._protocol = protocol.value

        @property
        def service_class(self):
            """
            The :class:`platypush.plugins.bluetooth.model.ServiceClass` enum
            value.
            """
            from platypush.plugins.bluetooth.model import ServiceClass

            try:
                return ServiceClass.get(self.uuid)
            except (TypeError, ValueError):
                return ServiceClass.UNKNOWN

        @override
        def to_dict(self) -> dict:
            return {
                **{k.lstrip('_'): v for k, v in super().to_dict().items()},
                # Human-readable service class name
                'service_class': str(self.service_class),
            }
