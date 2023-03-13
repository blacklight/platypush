from typing import Any, Dict, Iterable, List
from platypush.entities.bluetooth import BluetoothService

from ..._model import ServiceClass


# pylint: disable=too-few-public-methods
class BluetoothServicesBuilder:
    """
    Builds a list of :class:`platypush.entities.bluetooth.BluetoothService`
    entities from the list of dictionaries returned by
    ``bluetooth.find_services()``.
    """

    @classmethod
    def build(cls, services: Iterable[Dict[str, Any]]) -> List[BluetoothService]:
        """
        Parse the services exposed by the device from the raw pybluez data.
        """
        parsed_services = {}

        for srv in services:
            service_args = {
                key: srv.get(key) for key in ['name', 'description', 'port', 'protocol']
            }

            classes = srv.get('service-classes', [])
            versions = dict(srv.get('profiles', []))

            for srv_cls in classes:
                uuid = BluetoothService.to_uuid(srv_cls)
                parsed_service = parsed_services[uuid] = BluetoothService(
                    id=f'{srv["host"]}::{srv_cls}',
                    uuid=uuid,
                    version=versions.get(srv_cls),
                    **service_args,
                )

                # Ensure that the service name is always set
                if not parsed_service.name:
                    parsed_service.name = (
                        str(parsed_service.service_class)
                        if parsed_service.service_class != ServiceClass.UNKNOWN
                        else f'[{parsed_service.uuid}]'
                    )

        return list(parsed_services.values())
