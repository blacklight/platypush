import os

from datetime import datetime
from typing import Tuple, Union, List, Optional, Dict
from typing_extensions import override

import psutil

from platypush.entities import Entity
from platypush.entities.devices import Device
from platypush.entities.managers import EntityManager
from platypush.entities.sensors import NumericSensor, PercentSensor
from platypush.entities.system import (
    Cpu,
    CpuInfo as CpuInfoModel,
    CpuStats as CpuStatsModel,
    CpuTimes as CpuTimesModel,
    Disk as DiskModel,
    MemoryStats as MemoryStatsModel,
    NetworkInterface as NetworkInterfaceModel,
    SwapStats as SwapStatsModel,
)
from platypush.message.response.system import (
    SensorTemperatureResponse,
    SensorResponseList,
    SensorFanResponse,
    SensorBatteryResponse,
    ConnectedUserResponseList,
    ConnectUserResponse,
    ProcessResponseList,
    ProcessResponse,
)
from platypush.plugins import action
from platypush.plugins.sensor import SensorPlugin
from platypush.schemas.system import (
    ConnectionSchema,
    CpuFrequency,
    CpuFrequencySchema,
    CpuInfo,
    CpuInfoSchema,
    CpuStats,
    CpuStatsSchema,
    CpuTimes,
    CpuTimesSchema,
    Disk,
    DiskSchema,
    MemoryStats,
    MemoryStatsSchema,
    NetworkInterface,
    NetworkInterfaceSchema,
    SwapStats,
    SwapStatsSchema,
    SystemInfoSchema,
)


# pylint: disable=too-many-ancestors
class SystemPlugin(SensorPlugin, EntityManager):
    """
    Plugin to get system info.

    Requires:

        - **py-cpuinfo** (``pip install py-cpuinfo``) for CPU model and info.
        - **psutil** (``pip install psutil``) for CPU load and stats.

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__cpu_info: Optional[CpuInfo] = None

    @property
    def _cpu_info(self) -> CpuInfo:
        from cpuinfo import get_cpu_info

        if not self.__cpu_info:
            # The CPU information won't change while the process is running, so
            # it makes sense to cache it only once.
            self.__cpu_info = CpuInfoSchema().load(get_cpu_info())  # type: ignore

        return self.__cpu_info  # type: ignore

    @action
    def cpu_info(self):
        """
        Get CPU info.
        :return: .. schema:: system.CpuInfoSchema
        """
        return CpuInfoSchema().dump(self._cpu_info)

    @staticmethod
    def _load_cpu_times(times, many: bool) -> Union[CpuTimes, List[CpuTimes]]:
        return CpuTimesSchema().load(times, many=many)  # type: ignore

    @classmethod
    def _cpu_times_avg(cls, percent=True) -> CpuTimes:
        method = psutil.cpu_times_percent if percent else psutil.cpu_times
        times = method(percpu=False)
        return cls._load_cpu_times(times, many=False)  # type: ignore

    @classmethod
    def _cpu_times_per_cpu(cls, percent=True) -> List[CpuTimes]:
        method = psutil.cpu_times_percent if percent else psutil.cpu_times
        times = method(percpu=True)
        return cls._load_cpu_times(times, many=True)  # type: ignore

    @action
    def cpu_times(self, per_cpu=False, percent=True) -> Union[list, dict]:
        """
        Get the CPU times per status, either as absolute time or a percentage.

        :param per_cpu: Get per-CPU stats (default: False).
        :param percent: Get the stats in percentage (default: True).
        :return: If ``per_cpu=False``:

            .. schema:: system.CpuTimesSchema

        If ``per_cpu=True`` then a list will be returned, where each item
        identifies the CPU times of a core:

           .. schema:: system.CpuTimesSchema(many=True)

        """
        method = self._cpu_times_per_cpu if per_cpu else self._cpu_times_avg
        return CpuTimesSchema().dump(method(percent=percent), many=per_cpu)

    @action
    def cpu_percent(
        self, per_cpu: bool = False, interval: Optional[float] = None
    ) -> Union[float, List[float]]:
        """
        Get the CPU load percentage.

        :param per_cpu: Get per-CPU stats (default: False).
        :param interval: When *interval* is 0.0 or None compares system CPU times elapsed since last call or module
            import, returning immediately (non blocking). That means the first time this is called it will
            return a meaningless 0.0 value which you should ignore. In this case is recommended for accuracy that this
            function be called with at least 0.1 seconds between calls.
        :return: float if ``per_cpu=False``, ``list[float]`` otherwise.
        """
        percent = psutil.cpu_percent(percpu=per_cpu, interval=interval)

        if per_cpu:
            return list(percent)  # type: ignore
        return percent

    def _cpu_stats(self) -> CpuStats:
        stats = psutil.cpu_stats()
        return CpuStatsSchema().load(stats)  # type: ignore

    @action
    def cpu_stats(self) -> CpuStats:
        """
        Get CPU stats.

        :return: .. schema:: system.CpuStatsSchema
        """
        return CpuStatsSchema().dump(self._cpu_stats())  # type: ignore

    def _cpu_frequency_avg(self) -> CpuFrequency:
        freq = psutil.cpu_freq(percpu=False)
        return CpuFrequencySchema().load(freq)  # type: ignore

    def _cpu_frequency_per_cpu(self) -> List[CpuFrequency]:
        freq = psutil.cpu_freq(percpu=True)
        return CpuFrequencySchema().load(freq, many=True)  # type: ignore

    @action
    def cpu_frequency(
        self, per_cpu: bool = False
    ) -> Union[CpuFrequency, List[CpuFrequency]]:
        """
        Get the CPU frequency, in MHz.

        :param per_cpu: Get per-CPU stats (default: False).
        :return: If ``per_cpu=False``:

            .. schema:: system.CpuFrequencySchema

        If ``per_cpu=True`` then a list will be returned, where each item
        identifies the CPU times of a core:

           .. schema:: system.CpuFrequencySchema(many=True)

        """
        return self._cpu_frequency_per_cpu() if per_cpu else self._cpu_frequency_avg()

    @action
    def load_avg(self) -> Tuple[float, float, float]:
        """
        Get the average load as a vector that represents the load within the last 1, 5 and 15 minutes.
        """
        return psutil.getloadavg()

    def _mem_virtual(self) -> MemoryStats:
        return MemoryStatsSchema().load(psutil.virtual_memory())  # type: ignore

    @action
    def mem_virtual(self) -> dict:
        """
        Get the current virtual memory usage stats.

        :return: .. schema:: system.MemoryStatsSchema
        """
        return MemoryStatsSchema().dump(self._mem_virtual())  # type: ignore

    def _mem_swap(self) -> SwapStats:
        return SwapStatsSchema().load(psutil.swap_memory())  # type: ignore

    @action
    def mem_swap(self) -> dict:
        """
        Get the current swap memory usage stats.

        :return: .. schema:: system.SwapStatsSchema
        """
        return SwapStatsSchema().dump(self._mem_swap())  # type: ignore

    def _disk_info(self) -> List[Disk]:
        parts = {part.device: part._asdict() for part in psutil.disk_partitions()}
        basename_parts = {os.path.basename(part): part for part in parts}
        io_stats = {
            basename_parts[disk]: stats._asdict()
            for disk, stats in psutil.disk_io_counters(perdisk=True).items()
            if disk in basename_parts
        }

        usage = {
            disk: psutil.disk_usage(info['mountpoint'])._asdict()  # type: ignore
            for disk, info in parts.items()
        }

        return DiskSchema().load(  # type: ignore
            [
                {
                    **info,
                    **io_stats[part],
                    **usage[part],
                }
                for part, info in parts.items()
            ],
            many=True,
        )

    @action
    def disk_info(self):
        """
        Get information about the detected disks and partitions.

        :return: .. schema:: system.DiskSchema(many=True)
        """
        return DiskSchema().dump(self._disk_info(), many=True)

    def _network_info(self) -> List[NetworkInterface]:
        addrs = psutil.net_if_addrs()
        stats = psutil.net_if_stats()

        return NetworkInterfaceSchema().load(  # type: ignore
            [
                {
                    'interface': interface,
                    'addresses': addrs.get(interface, []),
                    **(stats[interface]._asdict() if stats.get(interface) else {}),
                    **info._asdict(),
                }
                for interface, info in psutil.net_io_counters(pernic=True).items()
                if any(bool(val) for val in info._asdict().values())
            ],
            many=True,
        )

    def _network_info_avg(self) -> NetworkInterface:
        stats = psutil.net_io_counters(pernic=False)
        return NetworkInterfaceSchema().load(  # type: ignore
            {
                'interface': None,
                **stats._asdict(),
            }
        )

    @action
    def network_info(self, per_nic: bool = False):
        """
        Get the information and statistics for the network interfaces.

        :param per_nic: Return the stats grouped by interface (default: False).
        :return: If ``per_nic=False``:

            .. schema:: system.NetworkInterfaceSchema

        If ``per_nic=True`` then a list will be returned, where each item
        identifies the statistics per network interface:

           .. schema:: system.NetworkInterfaceSchema(many=True)
        """

        if per_nic:
            return NetworkInterfaceSchema().dump(self._network_info(), many=True)
        return NetworkInterfaceSchema().dump(self._network_info_avg())

    @action
    def net_connections(self, type: str = 'inet') -> List[dict]:
        """
        Get the list of active network connections.
        On MacOS this function requires root privileges.

        :param type: Connection type to filter (default: ``inet``). Supported
            types:

            +------------+----------------------------------------------------+
            | ``type``   | Description                                        |
            +------------+----------------------------------------------------+
            | ``inet``   | IPv4 and IPv6                                      |
            | ``inet4``  | IPv4                                               |
            | ``inet6``  | IPv6                                               |
            | ``tcp``    | TCP                                                |
            | ``tcp4``   | TCP over IPv4                                      |
            | ``tcp6``   | TCP over IPv6                                      |
            | ``udp``    | UDP                                                |
            | ``udp4``   | UDP over IPv4                                      |
            | ``udp6``   | UDP over IPv6                                      |
            | ``unix``   | UNIX socket (both UDP and TCP protocols)           |
            | ``all``    | Any families and protocols                         |
            +------------+----------------------------------------------------+

        :return: .. schema:: system.ConnectionSchema(many=True)
        """
        schema = ConnectionSchema()
        return schema.dump(
            schema.load(psutil.net_connections(kind=type), many=True),  # type: ignore
            many=True,
        )

    @action
    def sensors_temperature(
        self, sensor: Optional[str] = None, fahrenheit: bool = False
    ) -> Union[
        SensorTemperatureResponse,
        List[SensorTemperatureResponse],
        Dict[str, Union[SensorTemperatureResponse, List[SensorTemperatureResponse]]],
    ]:
        """
        Get stats from the temperature sensors.

        :param sensor: Select the sensor name.
        :param fahrenheit: Return the temperature in Fahrenheit (default: Celsius).
        """
        stats = psutil.sensors_temperatures(fahrenheit=fahrenheit)

        if sensor:
            stats = [addr for name, addr in stats.items() if name == sensor]
            assert stats, 'No such sensor name: {}'.format(sensor)
            if len(stats) == 1:
                return SensorTemperatureResponse(
                    name=sensor,
                    current=stats[0].current,
                    high=stats[0].high,
                    critical=stats[0].critical,
                    label=stats[0].label,
                )

            return [
                SensorTemperatureResponse(
                    name=sensor,
                    current=s.current,
                    high=s.high,
                    critical=s.critical,
                    label=s.label,
                )
                for s in stats
            ]

        ret = {}
        for name, data in stats.items():
            for stat in data:
                resp = SensorTemperatureResponse(
                    name=sensor,
                    current=stat.current,
                    high=stat.high,
                    critical=stat.critical,
                    label=stat.label,
                ).output

                if name not in ret:
                    ret[name] = resp
                else:
                    if isinstance(ret[name], list):
                        ret[name].append(resp)
                    else:
                        ret[name] = [ret[name], resp]

        return ret

    @action
    def sensors_fan(self, sensor: Optional[str] = None) -> SensorResponseList:
        """
        Get stats from the fan sensors.

        :param sensor: Select the sensor name.
        :return: List of :class:`platypush.message.response.system.SensorFanResponse`.
        """
        stats = psutil.sensors_fans()

        def _expand_stats(name, _stats):
            return SensorResponseList(
                [
                    SensorFanResponse(
                        name=name,
                        current=s.current,
                        label=s.label,
                    )
                    for s in _stats
                ]
            )

        if sensor:
            stats = [addr for name, addr in stats.items() if name == sensor]
            assert stats, 'No such sensor name: {}'.format(sensor)
            return _expand_stats(sensor, stats[0])

        return SensorResponseList(
            [_expand_stats(name, stat) for name, stat in stats.items()]
        )

    @action
    def sensors_battery(self) -> SensorBatteryResponse:
        """
        Get stats from the battery sensor.
        :return: List of :class:`platypush.message.response.system.SensorFanResponse`.
        """
        stats = psutil.sensors_battery()

        return SensorBatteryResponse(
            percent=stats.percent,
            secs_left=stats.secsleft,
            power_plugged=stats.power_plugged,
        )

    @action
    def connected_users(self) -> ConnectedUserResponseList:
        """
        Get the list of connected users.
        :return: List of :class:`platypush.message.response.system.ConnectUserResponse`.
        """
        users = psutil.users()

        return ConnectedUserResponseList(
            [
                ConnectUserResponse(
                    name=u.name,
                    terminal=u.terminal,
                    host=u.host,
                    started=datetime.fromtimestamp(u.started),
                    pid=u.pid,
                )
                for u in users
            ]
        )

    @action
    def processes(self, filter: Optional[str] = '') -> ProcessResponseList:
        """
        Get the list of running processes.

        :param filter: Filter the list by name.
        :return: List of :class:`platypush.message.response.system.ProcessResponse`.
        """
        processes = [psutil.Process(pid) for pid in psutil.pids()]
        p_list = []

        for p in processes:
            if filter and filter not in p.name():
                continue

            args = {}

            try:
                mem = p.memory_info()
                times = p.cpu_times()
                args.update(
                    pid=p.pid,
                    name=p.name(),
                    started=datetime.fromtimestamp(p.create_time()),
                    ppid=p.ppid(),
                    children=[pp.pid for pp in p.children()],
                    status=p.status(),
                    username=p.username(),
                    terminal=p.terminal(),
                    cpu_user_time=times.user,
                    cpu_system_time=times.system,
                    cpu_children_user_time=times.children_user,
                    cpu_children_system_time=times.children_system,
                    mem_rss=mem.rss,
                    mem_vms=mem.vms,
                    mem_shared=mem.shared,
                    mem_text=mem.text,
                    mem_data=mem.data,
                    mem_lib=mem.lib,
                    mem_dirty=mem.dirty,
                    mem_percent=p.memory_percent(),
                )
            except psutil.Error:
                continue

            try:
                args.update(
                    exe=p.exe(),
                )
            except psutil.Error:
                pass

            p_list.append(ProcessResponse(**args))

        return ProcessResponseList(p_list)

    @staticmethod
    def _get_process(pid: int):
        return psutil.Process(pid)

    @action
    def pid_exists(self, pid: int) -> bool:
        """
        :param pid: Process PID.
        :return: ``True`` if the process exists, ``False`` otherwise.
        """
        return psutil.pid_exists(pid)

    @action
    def suspend(self, pid: int):
        """
        Suspend a process.
        :param pid: Process PID.
        """
        self._get_process(pid).suspend()

    @action
    def resume(self, pid: int):
        """
        Resume a process.
        :param pid: Process PID.
        """
        self._get_process(pid).resume()

    @action
    def terminate(self, pid: int):
        """
        Terminate a process.
        :param pid: Process PID.
        """
        self._get_process(pid).terminate()

    @action
    def kill(self, pid: int):
        """
        Kill a process.
        :param pid: Process PID.
        """
        self._get_process(pid).kill()

    @action
    def wait(self, pid: int, timeout: Optional[int] = None):
        """
        Wait for a process to terminate.

        :param pid: Process PID.
        :param timeout: Timeout in seconds (default: ``None``).
        """
        self._get_process(pid).wait(timeout)

    @override
    @action
    def get_measurement(self, *_, **__):
        """
        :return: .. schema:: system.SystemInfoSchema
        """
        ret = SystemInfoSchema().dump(
            {
                'cpu': {
                    'frequency': self._cpu_frequency_avg(),
                    'info': self._cpu_info,
                    'load_avg': self.load_avg().output,  # type: ignore
                    'stats': self._cpu_stats(),
                    'times': self._cpu_times_avg(),
                    'percent': self.cpu_percent().output / 100.0,  # type: ignore
                },
                'memory': self._mem_virtual(),
                'swap': self._mem_swap(),
                'disks': self._disk_info(),
                'network': self._network_info(),
            }
        )

        return ret

    @override
    def transform_entities(self, entities: dict) -> List[Entity]:
        cpu = entities['cpu'].copy()

        return [
            Cpu(
                id='system:cpu',
                name='CPU',
                percent=cpu['percent'],
                children=[
                    CpuInfoModel(
                        id='system:cpu:info',
                        name='Info',
                        **cpu['info'],
                    ),
                    CpuStatsModel(
                        id='system:cpu:stats',
                        name='Statistics',
                        children=[
                            NumericSensor(
                                id=f'system:cpu:stats:{key}',
                                name=key,
                                value=value,
                            )
                            for key, value in cpu['stats'].items()
                        ],
                    ),
                    CpuTimesModel(
                        id='system:cpu:times',
                        name='Times',
                        children=[
                            PercentSensor(
                                id=f'system:cpu:times:{key}',
                                name=key,
                                value=time_percent,
                            )
                            for key, time_percent in cpu['times'].items()
                        ],
                    ),
                    Device(
                        id='system:cpu:load_avg',
                        name='Load Average',
                        children=[
                            NumericSensor(
                                id=f'system:cpu:load_avg:{mins}',
                                name=f'Last {mins} minute(s)',
                                value=round(val, 2),
                            )
                            for val, mins in zip(cpu['load_avg'], [1, 5, 15])
                        ],
                    ),
                    NumericSensor(
                        id='system:cpu:frequency',
                        name='Frequency',
                        value=round(cpu['frequency']['current'], 2),
                        min=cpu['frequency']['min'],
                        max=cpu['frequency']['max'],
                        unit='MHz',
                    ),
                ],
            ),
            MemoryStatsModel(
                id='system:memory',
                name='Memory',
                **entities['memory'],
            ),
            SwapStatsModel(
                id='system:swap',
                name='Swap',
                **entities['swap'],
            ),
            *[
                DiskModel(
                    id=f'system:disk:{disk["device"]}',
                    name=disk.pop('device'),
                    **disk,
                )
                for disk in entities['disks']
            ],
            *[
                NetworkInterfaceModel(
                    id=f'system:network_interface:{nic["interface"]}',
                    name=nic.pop('interface'),
                    reachable=nic.pop('is_up'),
                    **nic,
                )
                for nic in entities['network']
            ],
        ]


# vim:sw=4:ts=4:et:
