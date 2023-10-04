from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, JSON, String

from platypush.common.db import is_defined

from . import Entity
from .devices import Device
from .sensors import NumericSensor, PercentSensor
from .temperature import TemperatureSensor


if not is_defined('cpu'):

    class Cpu(Entity):
        """
        ``CPU`` ORM (container) model.
        """

        __tablename__ = 'cpu'

        id = Column(
            Integer, ForeignKey(Entity.id, ondelete='CASCADE'), primary_key=True
        )

        percent = Column(Float)

        __table_args__ = {'extend_existing': True}
        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }


if not is_defined('cpu_info'):

    class CpuInfo(Entity):
        """
        ``CpuInfo`` ORM model.
        """

        __tablename__ = 'cpu_info'

        id = Column(
            Integer, ForeignKey(Entity.id, ondelete='CASCADE'), primary_key=True
        )

        architecture = Column(String)
        bits = Column(Integer)
        cores = Column(Integer)
        vendor = Column(String)
        brand = Column(String)
        frequency_advertised = Column(Integer)
        frequency_actual = Column(Integer)
        flags = Column(JSON)
        l1_instruction_cache_size = Column(Integer)
        l1_data_cache_size = Column(Integer)
        l2_cache_size = Column(Integer)
        l3_cache_size = Column(Integer)

        __table_args__ = {'extend_existing': True}
        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }


if not is_defined('cpu_times'):

    class CpuTimes(Entity):
        """
        ``CpuTimes`` ORM (container) model.
        """

        __tablename__ = 'cpu_times'

        id = Column(
            Integer, ForeignKey(Entity.id, ondelete='CASCADE'), primary_key=True
        )

        __table_args__ = {'extend_existing': True}
        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }


if not is_defined('cpu_stats'):

    class CpuStats(Entity):
        """
        ``CpuStats`` ORM (container) model.
        """

        __tablename__ = 'cpu_stats'

        id = Column(
            Integer, ForeignKey(Entity.id, ondelete='CASCADE'), primary_key=True
        )

        __table_args__ = {'extend_existing': True}
        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }


if not is_defined('memory_stats'):

    class MemoryStats(Entity):
        """
        ``MemoryStats`` ORM model.
        """

        __tablename__ = 'memory_stats'

        id = Column(
            Integer, ForeignKey(Entity.id, ondelete='CASCADE'), primary_key=True
        )

        total = Column(Integer)
        available = Column(Integer)
        used = Column(Integer)
        free = Column(Integer)
        active = Column(Integer)
        inactive = Column(Integer)
        buffers = Column(Integer)
        cached = Column(Integer)
        shared = Column(Integer)
        percent = Column(Float)

        __table_args__ = {'extend_existing': True}
        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }


if not is_defined('swap_stats'):

    class SwapStats(Entity):
        """
        ``SwapStats`` ORM model.
        """

        __tablename__ = 'swap_stats'

        id = Column(
            Integer, ForeignKey(Entity.id, ondelete='CASCADE'), primary_key=True
        )

        total = Column(Integer)
        used = Column(Integer)
        free = Column(Integer)
        percent = Column(Float)

        __table_args__ = {'extend_existing': True}
        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }


if not is_defined('disk'):

    class Disk(Entity):
        """
        ``Disk`` ORM model.
        """

        __tablename__ = 'disk'

        id = Column(
            Integer, ForeignKey(Entity.id, ondelete='CASCADE'), primary_key=True
        )

        mountpoint = Column(String)
        fstype = Column(String)
        opts = Column(String)
        total = Column(Integer)
        used = Column(Integer)
        free = Column(Integer)
        percent = Column(Float)
        read_count = Column(Integer)
        write_count = Column(Integer)
        read_bytes = Column(Integer)
        write_bytes = Column(Integer)
        read_time = Column(Float)
        write_time = Column(Float)
        busy_time = Column(Float)

        __table_args__ = {'extend_existing': True}
        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }


if not is_defined('network_interface'):

    class NetworkInterface(Device):
        """
        ``NetworkInterface`` ORM model.
        """

        __tablename__ = 'network_interface'

        id = Column(
            Integer, ForeignKey(Device.id, ondelete='CASCADE'), primary_key=True
        )

        bytes_sent = Column(Integer)
        bytes_recv = Column(Integer)
        packets_sent = Column(Integer)
        packets_recv = Column(Integer)
        errors_in = Column(Integer)
        errors_out = Column(Integer)
        drop_in = Column(Integer)
        drop_out = Column(Integer)
        addresses = Column(JSON)
        speed = Column(Integer)
        mtu = Column(Integer)
        duplex = Column(String)
        flags = Column(JSON)

        __table_args__ = {'extend_existing': True}
        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }


if not is_defined('system_temperature'):

    class SystemTemperature(TemperatureSensor):
        """
        Extends the ``TemperatureSensor``.
        """

        __tablename__ = 'system_temperature'

        id = Column(
            Integer,
            ForeignKey(TemperatureSensor.id, ondelete='CASCADE'),
            primary_key=True,
        )

        high = Column(Float)
        critical = Column(Float)

        __table_args__ = {'extend_existing': True}
        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }


if not is_defined('system_fan'):

    class SystemFan(NumericSensor):
        """
        ``SystemFan`` ORM model.
        """

        __tablename__ = 'system_fan'

        id = Column(
            Integer,
            ForeignKey(NumericSensor.id, ondelete='CASCADE'),
            primary_key=True,
        )

        __table_args__ = {'extend_existing': True}
        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }


if not is_defined('system_battery'):

    class SystemBattery(PercentSensor):
        """
        ``SystemBattery`` ORM model.
        """

        __tablename__ = 'system_battery'

        id = Column(
            Integer,
            ForeignKey(PercentSensor.id, ondelete='CASCADE'),
            primary_key=True,
        )

        seconds_left = Column(Float)
        power_plugged = Column(Boolean)

        __table_args__ = {'extend_existing': True}
        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }
