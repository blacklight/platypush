from enum import Enum
from typing import Any, Callable, List, Optional, Type, Union

from pysmartthings import Attribute, Capability, Command, DeviceEntity

from platypush.entities import Entity

from platypush.entities.audio import Muted, Volume
from platypush.entities.batteries import Battery
from platypush.entities.dimmers import Dimmer
from platypush.entities.electricity import EnergySensor, PowerSensor, VoltageSensor
from platypush.entities.humidity import HumiditySensor
from platypush.entities.illuminance import IlluminanceSensor
from platypush.entities.linkquality import LinkQuality
from platypush.entities.motion import MotionSensor
from platypush.entities.sensors import (
    BinarySensor,
    EnumSensor,
    CompositeSensor,
    NumericSensor,
)
from platypush.entities.switches import EnumSwitch, Switch
from platypush.entities.temperature import TemperatureSensor


class DeviceMapper:
    """
    The purpose of these objects is to map the capabilities of SmartThings
    devices to native Platypush entities.
    """

    def __init__(
        self,
        entity_type: Type[Entity],
        capability: str,
        attribute: str,
        value_type: Union[Type, Enum, str],
        set_command: Optional[Union[str, Callable[[Any], str]]] = None,
        get_value: Optional[Callable[[DeviceEntity], Any]] = None,
        set_value_args: Optional[Callable[..., Any]] = None,
        **kwargs
    ):
        self.entity_type = entity_type
        self.capability = capability
        self.set_command = set_command
        self.attribute = attribute
        self.value_type = value_type
        self.get_value = get_value if get_value else self._default_get_value
        self.values: List[str] = []
        self.entity_args = kwargs

        if isinstance(value_type, Enum):
            self.values = [v.name for v in entity_type]  # type: ignore

        self.set_value_args = (
            set_value_args if set_value_args else self._default_set_value_args
        )

    def _cast_value(self, value: Any) -> Any:
        if not isinstance(self.value_type, (str, Enum)):
            try:
                value = self.value_type(value)
            except Exception:
                # Set the value to None in case of cast errors
                value = None

        return value

    def _default_get_value(self, device: DeviceEntity) -> Any:
        if hasattr(device.status, self.attribute):
            value = getattr(device.status, self.attribute)
        else:
            value = device.status.attributes[self.attribute].value

        return self._cast_value(value)

    def _default_set_value_args(self, *values: Any) -> List[Any]:
        return [self._cast_value(v) for v in values]


device_mappers: List[DeviceMapper] = [
    # acceleration_sensor
    DeviceMapper(
        entity_type=BinarySensor,
        capability=Capability.acceleration_sensor,
        attribute=Attribute.acceleration,
        value_type=bool,
    ),
    # air_conditioner_fan_mode
    DeviceMapper(
        entity_type=EnumSwitch,
        capability=Capability.air_conditioner_fan_mode,
        attribute=Attribute.fan_mode,
        value_type=Attribute.supported_ac_fan_modes,
        set_command=Command.set_fan_mode,
    ),
    # air_conditioner_mode
    DeviceMapper(
        entity_type=EnumSwitch,
        capability=Capability.air_conditioner_mode,
        attribute=Attribute.air_conditioner_mode,
        value_type=Attribute.supported_ac_modes,
        set_command=Command.set_air_conditioner_mode,
    ),
    # air_quality_sensor
    DeviceMapper(
        entity_type=NumericSensor,
        capability=Capability.air_quality_sensor,
        attribute=Attribute.air_quality,
        value_type=int,
    ),
    # alarm
    DeviceMapper(
        entity_type=EnumSwitch,
        capability=Capability.alarm,
        attribute=Attribute.alarm,
        value_type=Enum('AlarmValues', ['both', 'off', 'siren', 'strobe']),
        set_command=lambda value: value,
        set_value_args=lambda *_: [],
    ),
    # audio_mute
    DeviceMapper(
        entity_type=Muted,
        capability=Capability.audio_mute,
        attribute=Attribute.mute,
        value_type=bool,
        set_command=lambda value: Command.mute if value else Command.unmute,
        set_value_args=lambda *_: [],
    ),
    # audio_volume
    DeviceMapper(
        entity_type=Volume,
        capability=Capability.audio_volume,
        attribute=Attribute.volume,
        value_type=int,
        set_command=Command.set_volume,
    ),
    # battery
    DeviceMapper(
        entity_type=Battery,
        capability=Capability.battery,
        attribute=Attribute.battery,
        value_type=int,
    ),
    # body_mass_index_measurement
    DeviceMapper(
        entity_type=NumericSensor,
        capability=Capability.body_mass_index_measurement,
        attribute=Attribute.body_weight_measurement,
        value_type=float,
    ),
    # body_weight_measurement
    DeviceMapper(
        entity_type=NumericSensor,
        capability=Capability.body_weight_measurement,
        attribute=Attribute.body_weight_measurement,
        value_type=float,
    ),
    # button
    DeviceMapper(
        entity_type=EnumSensor,
        capability=Capability.button,
        attribute=Attribute.button,
        value_type=Enum(
            'ButtonValues',
            [
                'pushed',
                'held',
                'double',
                'pushed_2x',
                'pushed_3x',
                'pushed_4x',
                'pushed_5x',
                'pushed_6x',
                'down',
                'down_2x',
                'down_3x',
                'down_4x',
                'down_5x',
                'down_6x',
                'down_hold',
                'up',
                'up_2x',
                'up_3x',
                'up_4x',
                'up_5x',
                'up_6x',
                'up_hold',
                'swipe_up',
                'swipe_down',
                'swipe_left',
                'swipe_right',
                'unknown',
            ],
        ),
    ),
    # carbon_dioxide_measurement
    DeviceMapper(
        entity_type=NumericSensor,
        capability=Capability.carbon_dioxide_measurement,
        attribute=Attribute.carbon_dioxide,
        value_type=float,
    ),
    # carbon_monoxide_detector
    DeviceMapper(
        entity_type=EnumSensor,
        capability=Capability.carbon_monoxide_detector,
        attribute=Attribute.carbon_monoxide,
        value_type=Enum(
            'CarbonMonoxideValues', ['clear', 'detected', 'tested', 'unknown']
        ),
    ),
    # carbon_monoxide_measurement
    DeviceMapper(
        entity_type=NumericSensor,
        capability=Capability.carbon_monoxide_measurement,
        attribute=Attribute.carbon_monoxide_level,
        value_type=float,
    ),
    # contact_sensor
    DeviceMapper(
        entity_type=BinarySensor,
        capability=Capability.contact_sensor,
        attribute=Attribute.contact,
        value_type=bool,
    ),
    # dishwasher_operating_state
    DeviceMapper(
        entity_type=EnumSensor,
        capability=Capability.dishwasher_operating_state,
        attribute=Attribute.machine_state,
        value_type=Attribute.supported_machine_states,
    ),
    # door_control
    DeviceMapper(
        entity_type=Switch,
        capability=Capability.door_control,
        attribute=Attribute.door,
        value_type=bool,
        get_value=lambda device: device.status.door in {'open', 'opening'},
        set_command=lambda value: Command.open if value else Command.close,
    ),
    # dryer_operating_state
    DeviceMapper(
        entity_type=EnumSensor,
        capability=Capability.dryer_operating_state,
        attribute=Attribute.machine_state,
        value_type=Attribute.supported_machine_states,
    ),
    # dust_sensor
    DeviceMapper(
        entity_type=NumericSensor,
        capability=Capability.dust_sensor,
        attribute=Attribute.dust_level,
        value_type=float,
    ),
    # energy_meter
    DeviceMapper(
        entity_type=EnergySensor,
        capability=Capability.energy_meter,
        attribute=Attribute.energy,
        value_type=float,
    ),
    # equivalent_carbon_dioxide_measurement
    DeviceMapper(
        entity_type=NumericSensor,
        capability=Capability.equivalent_carbon_dioxide_measurement,
        attribute=Attribute.equivalent_carbon_dioxide_measurement,
        value_type=float,
    ),
    # fan_speed
    DeviceMapper(
        entity_type=Dimmer,
        capability=Capability.fan_speed,
        attribute=Attribute.fan_speed,
        value_type=int,
        set_command=Command.set_fan_speed,
    ),
    # formaldehyde_measurement
    DeviceMapper(
        entity_type=NumericSensor,
        capability=Capability.formaldehyde_measurement,
        attribute=Attribute.formaldehyde_level,
        value_type=float,
    ),
    # gas_meter
    DeviceMapper(
        entity_type=NumericSensor,
        capability=Capability.gas_meter,
        attribute=Attribute.gas_meter,
        value_type=float,
    ),
    # illuminance_measurement
    DeviceMapper(
        entity_type=IlluminanceSensor,
        capability=Capability.illuminance_measurement,
        attribute=Attribute.illuminance,
        value_type=float,
    ),
    # infrared_level
    DeviceMapper(
        entity_type=NumericSensor,
        capability=Capability.infrared_level,
        attribute=Attribute.infrared_level,
        value_type=int,
        min=0,
        max=100,
    ),
    # lock
    DeviceMapper(
        entity_type=Switch,
        capability=Capability.lock,
        attribute=Attribute.lock,
        value_type=bool,
        get_value=lambda device: device.status.lock in {True, 'locked'},
        set_command=lambda value: Command.lock if value else Command.unlock,
        set_value_args=lambda *_: [],
    ),
    # media_input_source
    DeviceMapper(
        entity_type=EnumSwitch,
        capability=Capability.media_input_source,
        attribute=Attribute.input_source,
        value_type=Attribute.supported_input_sources,
        set_command=Command.set_input_source,
    ),
    # motion_sensor
    DeviceMapper(
        entity_type=MotionSensor,
        capability=Capability.motion_sensor,
        attribute=Attribute.motion,
        value_type=bool,
    ),
    # odor_sensor
    DeviceMapper(
        entity_type=NumericSensor,
        capability=Capability.odor_sensor,
        attribute=Attribute.odor_level,
        value_type=int,
    ),
    # oven_operating_state
    DeviceMapper(
        entity_type=EnumSensor,
        capability=Capability.oven_operating_state,
        attribute=Attribute.machine_state,
        value_type=Attribute.supported_machine_states,
    ),
    # power_consumption_report
    DeviceMapper(
        entity_type=PowerSensor,
        capability=Capability.power_consumption_report,
        attribute=Attribute.power_consumption,
        value_type=float,
    ),
    # power_meter
    DeviceMapper(
        entity_type=PowerSensor,
        capability=Capability.power_meter,
        attribute=Attribute.power,
        value_type=float,
    ),
    # power_source
    DeviceMapper(
        entity_type=EnumSensor,
        capability=Capability.power_source,
        attribute=Attribute.power_source,
        value_type=Enum('PowerSourceValues', ['battery', 'dc', 'mains', 'unknown']),
    ),
    # presence_sensor
    DeviceMapper(
        entity_type=BinarySensor,
        capability=Capability.presence_sensor,
        attribute=Attribute.presence,
        value_type=bool,
    ),
    # relative_humidity_measurement
    DeviceMapper(
        entity_type=HumiditySensor,
        capability=Capability.relative_humidity_measurement,
        attribute=Attribute.humidity,
        value_type=int,
        min=0,
        max=100,
    ),
    # signal_strength
    DeviceMapper(
        entity_type=LinkQuality,
        capability=Capability.signal_strength,
        attribute=Attribute.lqi,
        value_type=int,
        min=0,
        max=255,
    ),
    # smoke_detector
    DeviceMapper(
        entity_type=EnumSensor,
        capability=Capability.smoke_detector,
        attribute=Attribute.smoke,
        value_type=Enum('SmokeDetectorValues', ['clear', 'detected', 'tested']),
    ),
    # sound_sensor
    DeviceMapper(
        entity_type=BinarySensor,
        capability=Capability.sound_sensor,
        attribute=Attribute.sound,
        value_type=bool,
    ),
    # switch
    DeviceMapper(
        entity_type=Switch,
        capability=Capability.switch,
        attribute=Attribute.switch,
        value_type=bool,
        set_command=lambda value: Command.on if value else Command.off,
        set_value_args=lambda *_: [],
    ),
    # switch_level
    DeviceMapper(
        entity_type=Dimmer,
        capability=Capability.switch_level,
        attribute=Attribute.level,
        value_type=int,
        set_command=Command.set_level,
    ),
    # tamper_alert
    DeviceMapper(
        entity_type=BinarySensor,
        capability=Capability.tamper_alert,
        attribute=Attribute.tamper,
        value_type=bool,
    ),
    # temperature_measurement
    DeviceMapper(
        entity_type=TemperatureSensor,
        capability=Capability.temperature_measurement,
        attribute=Attribute.temperature,
        value_type=float,
    ),
    # thermostat_cooling_setpoint
    DeviceMapper(
        entity_type=Dimmer,
        capability=Capability.thermostat_cooling_setpoint,
        attribute=Attribute.cooling_setpoint,
        value_type=float,
        min=-460,
        max=10000,
        set_command=Command.set_cooling_setpoint,
    ),
    # thermostat_fan_mode
    DeviceMapper(
        entity_type=EnumSwitch,
        capability=Capability.thermostat_fan_mode,
        attribute=Attribute.thermostat_fan_mode,
        value_type=Attribute.supported_thermostat_fan_modes,
        set_command=Command.set_thermostat_fan_mode,
    ),
    # thermostat_heating_setpoint
    DeviceMapper(
        entity_type=Dimmer,
        capability=Capability.thermostat_heating_setpoint,
        attribute=Attribute.heating_setpoint,
        value_type=float,
        min=-460,
        max=10000,
        set_command=Command.set_heating_setpoint,
    ),
    # thermostat_mode
    DeviceMapper(
        entity_type=EnumSwitch,
        capability=Capability.thermostat_mode,
        attribute=Attribute.thermostat_mode,
        value_type=Attribute.supported_thermostat_modes,
        set_command=Command.set_thermostat_mode,
    ),
    # thermostat_operating_state
    DeviceMapper(
        entity_type=EnumSensor,
        capability=Capability.thermostat_operating_state,
        attribute=Attribute.thermostat_operating_state,
        value_type=Enum(
            'ThermostatOperatingState',
            [
                'cooling',
                'fan only',
                'heating',
                'idle',
                'pending cool',
                'pending heat',
                'vent economizer',
            ],
        ),
    ),
    # three_axis
    DeviceMapper(
        entity_type=CompositeSensor,
        capability=Capability.three_axis,
        attribute=Attribute.three_axis,
        value_type=list,
    ),
    # tv_channel
    DeviceMapper(
        entity_type=Dimmer,
        capability=Capability.tv_channel,
        attribute=Attribute.tv_channel,
        value_type=int,
        set_command=Command.set_tv_channel,
        min=1,
        max=1000,
    ),
    # tvoc_measurement
    DeviceMapper(
        entity_type=NumericSensor,
        capability=Capability.tvoc_measurement,
        attribute=Attribute.tvoc_level,
        value_type=float,
    ),
    # ultraviolet_index
    DeviceMapper(
        entity_type=NumericSensor,
        capability=Capability.ultraviolet_index,
        attribute=Attribute.ultraviolet_index,
        value_type=float,
    ),
    # valve
    DeviceMapper(
        entity_type=Switch,
        capability=Capability.valve,
        attribute=Attribute.valve,
        value_type=bool,
        set_command=lambda value: Command.open if value else Command.close,
        set_value_args=lambda *_: [],
    ),
    # voltage_measurement
    DeviceMapper(
        entity_type=VoltageSensor,
        capability=Capability.voltage_measurement,
        attribute=Attribute.voltage,
        value_type=float,
    ),
    # washer_operating_state
    DeviceMapper(
        entity_type=EnumSensor,
        capability=Capability.washer_operating_state,
        attribute=Attribute.machine_state,
        value_type=Attribute.supported_machine_states,
    ),
    # water_sensor
    DeviceMapper(
        entity_type=BinarySensor,
        capability=Capability.water_sensor,
        attribute=Attribute.water,
        value_type=bool,
    ),
    # window_shade
    DeviceMapper(
        entity_type=Dimmer,
        capability=Capability.window_shade,
        attribute=Attribute.window_shade,
        value_type=int,
        set_command='setWindowShade',
        min=0,
        max=100,
    ),
]


# vim:sw=4:ts=4:et:
