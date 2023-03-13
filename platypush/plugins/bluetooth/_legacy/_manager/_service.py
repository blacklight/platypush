from concurrent.futures import ProcessPoolExecutor
from logging import getLogger
from typing import Dict, List, Optional

import bluetooth

from platypush.entities.bluetooth import BluetoothService

from .._model import BluetoothServicesBuilder


# pylint: disable=too-few-public-methods
class ServiceDiscoverer:
    """
    Runs the service discovery processes in a pool.
    """

    def __init__(self, max_workers: int = 4, timeout: float = 30):
        self._max_workers = max_workers
        self._timeout = timeout
        self.logger = getLogger(__name__)

    def _discover(self, address: str) -> List[BluetoothService]:
        """
        Inner implementation of the service discovery for a specific device.
        """
        self.logger.info("Discovering services for %s...", address)
        try:
            return BluetoothServicesBuilder.build(
                bluetooth.find_service(address=address)
            )
        except Exception as e:
            self.logger.warning(
                "Failed to discover services for the device %s: %s", address, e
            )
            return []
        finally:
            self.logger.info("Service discovery for %s completed", address)

    def discover(
        self, *addresses: str, timeout: Optional[float] = None
    ) -> Dict[str, List[BluetoothService]]:
        """
        Discover the services for the given addresses. Discovery will happen in
        parallel through a process pool.

        :param addresses: The addresses to scan.
        :param timeout: The timeout in seconds.
        :return: An ``{address: [services]}`` dictionary with the discovered
            services per device.
        """
        discovered_services: Dict[str, List[BluetoothService]] = {}
        with ProcessPoolExecutor(max_workers=self._max_workers) as executor:
            try:
                for i, services in enumerate(
                    executor.map(
                        self._discover, addresses, timeout=timeout or self._timeout
                    )
                ):
                    discovered_services[addresses[i]] = services
            except TimeoutError:
                self.logger.warning("Service discovery timed out.")

        return discovered_services
