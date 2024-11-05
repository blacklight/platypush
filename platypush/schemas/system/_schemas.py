from marshmallow import fields

from ._base import SystemBaseSchema
from ._battery import BatterySchema
from ._cpu import CpuSchema
from ._disk import DiskSchema
from ._fan import FanSchema
from ._memory import MemoryStatsSchema, SwapStatsSchema
from ._network import NetworkInterfaceSchema
from ._temperature import TemperatureSchema


class SystemInfoSchema(SystemBaseSchema):
    """
    Schema for system info.
    """

    cpu = fields.Nested(CpuSchema)
    memory = fields.Nested(MemoryStatsSchema)
    swap = fields.Nested(SwapStatsSchema)
    disks = fields.List(fields.Nested(DiskSchema))
    network = fields.List(fields.Nested(NetworkInterfaceSchema))
    temperature = fields.List(fields.Nested(TemperatureSchema))
    fans = fields.List(fields.Nested(FanSchema))
    battery = fields.Nested(BatterySchema)
