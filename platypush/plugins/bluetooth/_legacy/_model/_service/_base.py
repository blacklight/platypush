from dataclasses import dataclass
from typing import Any, Dict, Iterable, Optional, Set, Tuple
from uuid import UUID

from .._protocol import Protocol
from ._directory import ServiceClass
from ._types import RawServiceClass

VersionedServices = Dict[ServiceClass, Optional[int]]
""" Service -> Version mapping. """


@dataclass
class BluetoothService:
    """
    Models a discovered Bluetooth service.
    """

    address: str
    """ The address of the service that exposes the service. """
    port: int
    """ The Bluetooth port associated to the service. """
    protocol: Protocol
    """ The service protocol. """
    name: Optional[str]
    """ The name of the service. """
    description: Optional[str]
    """ The description of the service. """
    service_id: Optional[str]
    """ The ID of the service. """
    service_classes: VersionedServices
    """
    The compatible classes exposed by the service - see
    https://btprodspecificationrefs.blob.core.windows.net/assigned-numbers/Assigned%20Number%20Types/Assigned%20Numbers.pdf,
    Section 5.
    """
    unknown_service_classes: Iterable[RawServiceClass]
    """ Service classes that are not supported. """

    @classmethod
    def build(cls, service: Dict[str, Any]) -> 'BluetoothService':
        """
        Builds a :class:`BluetoothService` from a service dictionary returned by
        pybluez.
        """
        return cls(
            address=service['host'],
            port=service['port'],
            protocol=Protocol(service['protocol']),
            name=service['name'],
            description=service['description'],
            service_id=service['service-id'],
            service_classes=cls._parse_services(
                service['service-classes'], service['profiles']
            ),
            unknown_service_classes=cls._parse_unknown_services(
                service['service-classes'],
            ),
        )

    @classmethod
    def _parse_services(
        cls, service_classes: Iterable[str], profiles: Iterable[Tuple[str, int]]
    ) -> VersionedServices:
        """
        Parses the services.

        :param service_classes: The service classes returned by pybluez.
        :param profiles: The profiles returned by pybluez as a list of
            ``[(service, version)]`` tuples.
        :return: A list of parsed service classes.
        """
        # Parse the service classes
        parsed_services: Dict[RawServiceClass, ServiceClass] = {}
        for srv in service_classes:
            srv_class = cls._parse_service_class(srv)
            parsed_services[srv_class.value] = srv_class

        # Parse the service classes versions
        versioned_classes: VersionedServices = {}
        for srv, version in profiles:
            value = cls._parse_service_class(srv).value
            parsed_srv = parsed_services.get(value)
            if parsed_srv:
                versioned_classes[parsed_srv] = version

        return {
            srv: versioned_classes.get(srv)
            for srv in parsed_services.values()
            if srv != ServiceClass.UNKNOWN
        }

    @classmethod
    def _parse_unknown_services(
        cls, service_classes: Iterable[str]
    ) -> Set[RawServiceClass]:
        return {
            cls._uuid(srv)
            for srv in service_classes
            if cls._parse_service_class(srv) == ServiceClass.UNKNOWN
        }

    @classmethod
    def _parse_service_class(cls, srv: str) -> ServiceClass:
        """
        :param srv: The service class returned by pybluez as a string (either
           hex-encoded or UUID).
        :return: The parsed :class:`ServiceClass` object or ``ServiceClass.UNKNOWN``.
        """
        srv_class: ServiceClass = ServiceClass.UNKNOWN
        try:
            srv_class = ServiceClass.get(cls._uuid(srv))
        except (TypeError, ValueError):
            pass

        return srv_class

    @staticmethod
    def _uuid(s: str) -> RawServiceClass:
        """
        :param s: The service class returned by pybluez as a string.
        :return: The UUID of the service class as a 16-bit or 128-bit identifier.
        """
        try:
            return UUID(s)
        except ValueError:
            return int(s, 16)
