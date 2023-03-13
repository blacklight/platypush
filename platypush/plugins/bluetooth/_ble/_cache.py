from typing import Dict, Iterable, Optional, Tuple
from typing_extensions import override

from bleak.backends.device import BLEDevice

from .._cache import BaseCache


class DeviceCache(BaseCache):
    """
    Cache used to store scanned Bluetooth devices as :class:`BLEDevice`.
    """

    _by_address: Dict[str, BLEDevice]
    _by_name: Dict[str, BLEDevice]

    @property
    @override
    def _address_field(self) -> str:
        return 'address'

    @property
    @override
    def _name_field(self) -> str:
        return 'name'

    @override
    def get(self, device: str) -> Optional[BLEDevice]:
        return super().get(device)

    @override
    def add(self, device: BLEDevice) -> BLEDevice:
        return super().add(device)

    @override
    def values(self) -> Iterable[BLEDevice]:
        return super().values()

    @override
    def items(self) -> Iterable[Tuple[str, BLEDevice]]:
        return super().items()
