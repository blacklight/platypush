from typing import Dict, Iterable, Optional, Tuple

from bleak.backends.device import BLEDevice

from .._cache import BaseCache


class DeviceCache(BaseCache):
    """
    Cache used to store scanned Bluetooth devices as :class:`BLEDevice`.
    """

    _by_address: Dict[str, BLEDevice]
    _by_name: Dict[str, BLEDevice]

    @property
    def _address_field(self) -> str:
        return 'address'

    @property
    def _name_field(self) -> str:
        return 'name'

    def get(self, device: str) -> Optional[BLEDevice]:
        return super().get(device)

    def add(self, device: BLEDevice) -> BLEDevice:
        return super().add(device)

    def values(self) -> Iterable[BLEDevice]:
        return super().values()

    def items(self) -> Iterable[Tuple[str, BLEDevice]]:
        return super().items()
