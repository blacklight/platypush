import socket

from datetime import datetime
from typing import Tuple, Union, List, Optional, Dict
from typing_extensions import override

from platypush.entities import Entity
from platypush.entities.devices import Device
from platypush.entities.managers import EntityManager
from platypush.entities.sensors import NumericSensor, PercentSensor
from platypush.entities.system import (
    Cpu,
    CpuInfo as CpuInfoModel,
    CpuStats as CpuStatsModel,
    CpuTimes as CpuTimesModel,
    MemoryStats as MemoryStatsModel,
    SwapStats as SwapStatsModel,
)
from platypush.message.response.system import (
    DiskResponseList,
    DiskPartitionResponse,
    DiskUsageResponse,
    DiskIoCountersResponse,
    NetworkIoCountersResponse,
    NetworkResponseList,
    NetworkConnectionResponse,
    NetworkAddressResponse,
    NetworkInterfaceStatsResponse,
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
    CpuFrequency,
    CpuFrequencySchema,
    CpuInfo,
    CpuInfoSchema,
    CpuStats,
    CpuStatsSchema,
    CpuTimes,
    CpuTimesSchema,
    MemoryStats,
    MemoryStatsSchema,
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
        import psutil

        method = psutil.cpu_times_percent if percent else psutil.cpu_times
        times = method(percpu=False)
        return cls._load_cpu_times(times, many=False)  # type: ignore

    @classmethod
    def _cpu_times_per_cpu(cls, percent=True) -> List[CpuTimes]:
        import psutil

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
        import psutil

        percent = psutil.cpu_percent(percpu=per_cpu, interval=interval)

        if per_cpu:
            return list(percent)  # type: ignore
        return percent

    def _cpu_stats(self) -> CpuStats:
        import psutil

        stats = psutil.cpu_stats()
        return CpuStatsSchema().load(stats._asdict())  # type: ignore

    @action
    def cpu_stats(self) -> CpuStats:
        """
        Get CPU stats.

        :return: .. schema:: system.CpuStatsSchema
        """
        return CpuStatsSchema().dump(self._cpu_stats())  # type: ignore

    def _cpu_frequency_avg(self) -> CpuFrequency:
        import psutil

        freq = psutil.cpu_freq(percpu=False)
        return CpuFrequencySchema().load(freq._asdict())  # type: ignore

    def _cpu_frequency_per_cpu(self) -> List[CpuFrequency]:
        import psutil

        freq = psutil.cpu_freq(percpu=True)
        return CpuFrequencySchema().load(freq._asdict(), many=True)  # type: ignore

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
        import psutil

        return psutil.getloadavg()

    def _mem_virtual(self) -> MemoryStats:
        import psutil

        return MemoryStatsSchema().load(
            psutil.virtual_memory()._asdict()
        )  # type: ignore

    @action
    def mem_virtual(self) -> dict:
        """
        Get the current virtual memory usage stats.

        :return: .. schema:: system.MemoryStatsSchema
        """
        return MemoryStatsSchema().dump(self._mem_virtual())  # type: ignore

    def _mem_swap(self) -> SwapStats:
        import psutil

        return SwapStatsSchema().load(psutil.swap_memory()._asdict())  # type: ignore

    @action
    def mem_swap(self) -> dict:
        """
        Get the current swap memory usage stats.

        :return: .. schema:: system.SwapStatsSchema
        """
        return SwapStatsSchema().dump(self._mem_swap())  # type: ignore

    @action
    def disk_partitions(self) -> DiskResponseList:
        """
        Get the list of partitions mounted on the system.
        :return: list of :class:`platypush.message.response.system.DiskPartitionResponse`
        """
        import psutil

        parts = psutil.disk_partitions()
        return DiskResponseList(
            [
                DiskPartitionResponse(
                    device=p.device,
                    mount_point=p.mountpoint,
                    fstype=p.fstype,
                    opts=p.opts,
                )
                for p in parts
            ]
        )

    @action
    def disk_usage(
        self, path: Optional[str] = None
    ) -> Union[DiskUsageResponse, DiskResponseList]:
        """
        Get the usage of a mounted disk.

        :param path: Path where the device is mounted (default: get stats for all mounted devices).
        :return: :class:`platypush.message.response.system.DiskUsageResponse` or list of
            :class:`platypush.message.response.system.DiskUsageResponse`.
        """
        import psutil

        if path:
            usage = psutil.disk_usage(path)
            return DiskUsageResponse(
                path=path,
                total=usage.total,
                used=usage.used,
                free=usage.free,
                percent=usage.percent,
            )
        else:
            disks = {
                p.mountpoint: psutil.disk_usage(p.mountpoint)
                for p in psutil.disk_partitions()
            }

            return DiskResponseList(
                [
                    DiskUsageResponse(
                        path=path,
                        total=disk.total,
                        used=disk.used,
                        free=disk.free,
                        percent=disk.percent,
                    )
                    for path, disk in disks.items()
                ]
            )

    @action
    def disk_io_counters(
        self, disk: Optional[str] = None, per_disk: bool = False
    ) -> Union[DiskIoCountersResponse, DiskResponseList]:
        """
        Get the I/O counter stats for the mounted disks.

        :param disk: Select the stats for a specific disk (e.g. 'sda1'). Default: get stats for all mounted disks.
        :param per_disk: Return the stats per disk (default: False).
        :return: :class:`platypush.message.response.system.DiskIoCountersResponse` or list of
            :class:`platypush.message.response.system.DiskIoCountersResponse`.
        """
        import psutil

        def _expand_response(_disk, _stats):
            return DiskIoCountersResponse(
                read_count=_stats.read_count,
                write_count=_stats.write_count,
                read_bytes=_stats.read_bytes,
                write_bytes=_stats.write_bytes,
                read_time=_stats.read_time,
                write_time=_stats.write_time,
                read_merged_count=_stats.read_merged_count,
                write_merged_count=_stats.write_merged_count,
                busy_time=_stats.busy_time,
                disk=_disk,
            )

        if disk:
            per_disk = True

        io = psutil.disk_io_counters(perdisk=per_disk)
        if disk:
            stats = [d for name, d in io.items() if name == disk]
            assert stats, 'No such disk: {}'.format(disk)
            return _expand_response(disk, stats[0])

        if not per_disk:
            return _expand_response(None, io)

        return DiskResponseList(
            [_expand_response(disk, stats) for disk, stats in io.items()]
        )

    @action
    def net_io_counters(
        self, nic: Optional[str] = None, per_nic: bool = False
    ) -> Union[NetworkIoCountersResponse, NetworkResponseList]:
        """
        Get the I/O counters stats for the network interfaces.

        :param nic: Select the stats for a specific network device (e.g. 'eth0'). Default: get stats for all NICs.
        :param per_nic: Return the stats broken down per interface (default: False).
        :return: :class:`platypush.message.response.system.NetIoCountersResponse` or list of
            :class:`platypush.message.response.system.NetIoCountersResponse`.
        """
        import psutil

        def _expand_response(_nic, _stats):
            return NetworkIoCountersResponse(
                bytes_sent=_stats.bytes_sent,
                bytes_recv=_stats.bytes_recv,
                packets_sent=_stats.packets_sent,
                packets_recv=_stats.packets_recv,
                errin=_stats.errin,
                errout=_stats.errout,
                dropin=_stats.dropin,
                dropout=_stats.dropout,
                nic=_nic,
            )

        if nic:
            per_nic = True

        io = psutil.net_io_counters(pernic=per_nic)
        if nic:
            stats = [d for name, d in io.items() if name == nic]
            assert stats, 'No such network interface: {}'.format(nic)
            return _expand_response(nic, stats[0])

        if not per_nic:
            return _expand_response(nic, io)

        return NetworkResponseList(
            [_expand_response(nic, stats) for nic, stats in io.items()]
        )

    @action
    def net_connections(
        self, type: Optional[str] = None
    ) -> Union[NetworkConnectionResponse, NetworkResponseList]:
        """
        Get the list of active network connections.
        On macOS this function requires root privileges.

        :param type: Connection type to filter. Supported types:

            +------------+----------------------------------------------------+
            | Kind Value | Connections using                                  |
            +------------+----------------------------------------------------+
            | inet       | IPv4 and IPv6                                      |
            | inet4      | IPv4                                               |
            | inet6      | IPv6                                               |
            | tcp        | TCP                                                |
            | tcp4       | TCP over IPv4                                      |
            | tcp6       | TCP over IPv6                                      |
            | udp        | UDP                                                |
            | udp4       | UDP over IPv4                                      |
            | udp6       | UDP over IPv6                                      |
            | unix       | UNIX socket (both UDP and TCP protocols)           |
            | all        | the sum of all the possible families and protocols |
            +------------+----------------------------------------------------+

        :return: List of :class:`platypush.message.response.system.NetworkConnectionResponse`.
        """
        import psutil

        conns = psutil.net_connections(kind=type)

        return NetworkResponseList(
            [
                NetworkConnectionResponse(
                    fd=conn.fd,
                    family=conn.family.name,
                    type=conn.type.name,
                    local_address=conn.laddr[0] if conn.laddr else None,
                    local_port=conn.laddr[1] if len(conn.laddr) > 1 else None,
                    remote_address=conn.raddr[0] if conn.raddr else None,
                    remote_port=conn.raddr[1] if len(conn.raddr) > 1 else None,
                    status=conn.status,
                    pid=conn.pid,
                )
                for conn in conns
            ]
        )

    @action
    def net_addresses(
        self, nic: Optional[str] = None
    ) -> Union[NetworkAddressResponse, NetworkResponseList]:
        """
        Get address info associated to the network interfaces.

        :param nic: Select the stats for a specific network device (e.g. 'eth0'). Default: get stats for all NICs.
        :return: :class:`platypush.message.response.system.NetworkAddressResponse` or list of
            :class:`platypush.message.response.system.NetworkAddressResponse`.
        """
        import psutil

        addrs = psutil.net_if_addrs()

        def _expand_addresses(_nic, _addrs):
            args = {'nic': _nic}

            for addr in _addrs:
                if addr.family == socket.AddressFamily.AF_INET:
                    args.update(
                        {
                            'ipv4_address': addr.address,
                            'ipv4_netmask': addr.netmask,
                            'ipv4_broadcast': addr.broadcast,
                        }
                    )
                elif addr.family == socket.AddressFamily.AF_INET6:
                    args.update(
                        {
                            'ipv6_address': addr.address,
                            'ipv6_netmask': addr.netmask,
                            'ipv6_broadcast': addr.broadcast,
                        }
                    )
                elif addr.family == socket.AddressFamily.AF_PACKET:
                    args.update(
                        {
                            'mac_address': addr.address,
                            'mac_broadcast': addr.broadcast,
                        }
                    )

                if addr.ptp and not args.get('ptp'):
                    args['ptp'] = addr.ptp

            return NetworkAddressResponse(**args)

        if nic:
            addrs = [addr for name, addr in addrs.items() if name == nic]
            assert addrs, 'No such network interface: {}'.format(nic)
            addr = addrs[0]
            return _expand_addresses(nic, addr)

        return NetworkResponseList(
            [_expand_addresses(nic, addr) for nic, addr in addrs.items()]
        )

    @action
    def net_stats(
        self, nic: Optional[str] = None
    ) -> Union[NetworkInterfaceStatsResponse, NetworkResponseList]:
        """
        Get stats about the network interfaces.

        :param nic: Select the stats for a specific network device (e.g. 'eth0'). Default: get stats for all NICs.
        :return: :class:`platypush.message.response.system.NetworkInterfaceStatsResponse` or list of
            :class:`platypush.message.response.system.NetworkInterfaceStatsResponse`.
        """
        import psutil

        stats = psutil.net_if_stats()

        def _expand_stats(_nic, _stats):
            return NetworkInterfaceStatsResponse(
                nic=_nic,
                is_up=_stats.isup,
                duplex=_stats.duplex.name,
                speed=_stats.speed,
                mtu=_stats.mtu,
            )

        if nic:
            stats = [addr for name, addr in stats.items() if name == nic]
            assert stats, 'No such network interface: {}'.format(nic)
            return _expand_stats(nic, stats[0])

        return NetworkResponseList(
            [_expand_stats(nic, addr) for nic, addr in stats.items()]
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
        import psutil

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
        import psutil

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
        import psutil

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
        import psutil

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
        import psutil

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
        import psutil

        return psutil.Process(pid)

    @action
    def pid_exists(self, pid: int) -> bool:
        """
        :param pid: Process PID.
        :return: ``True`` if the process exists, ``False`` otherwise.
        """
        import psutil

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
                    PercentSensor(
                        id='system:cpu:percent',
                        name='Percent',
                        value=cpu['percent'],
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
        ]


# vim:sw=4:ts=4:et:
