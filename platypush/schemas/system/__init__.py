from ._battery import Battery, BatterySchema
from ._connection import Connection, ConnectionSchema
from ._cpu import (
    Cpu,
    CpuFrequency,
    CpuFrequencySchema,
    CpuInfo,
    CpuInfoSchema,
    CpuStats,
    CpuStatsSchema,
    CpuTimes,
    CpuTimesSchema,
)
from ._disk import Disk, DiskSchema
from ._fan import Fan, FanSchema
from ._memory import MemoryStats, MemoryStatsSchema, SwapStats, SwapStatsSchema
from ._model import SystemInfo
from ._network import NetworkInterface, NetworkInterfaceSchema
from ._process import Process, ProcessSchema
from ._schemas import SystemInfoSchema
from ._temperature import Temperature, TemperatureSchema
from ._user import User, UserSchema


__all__ = [
    "Battery",
    "BatterySchema",
    "Connection",
    "ConnectionSchema",
    "Cpu",
    "CpuFrequency",
    "CpuFrequencySchema",
    "CpuInfo",
    "CpuInfoSchema",
    "CpuStats",
    "CpuStatsSchema",
    "CpuTimes",
    "CpuTimesSchema",
    "Disk",
    "DiskSchema",
    "Fan",
    "FanSchema",
    "MemoryStats",
    "MemoryStatsSchema",
    "Process",
    "ProcessSchema",
    "SwapStats",
    "SwapStatsSchema",
    "NetworkInterface",
    "NetworkInterfaceSchema",
    "SystemInfo",
    "SystemInfoSchema",
    "Temperature",
    "TemperatureSchema",
    "User",
    "UserSchema",
]
