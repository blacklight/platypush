import json
import struct
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData
from bluetooth_numbers import company, oui

from TheengsDecoder import decodeBLE, getAttribute, getProperties

from platypush.entities import Entity
from platypush.entities.batteries import Battery
from platypush.entities.bluetooth import BluetoothDevice, BluetoothService
from platypush.entities.contact import ContactSensor
from platypush.entities.electricity import (
    CurrentSensor,
    EnergySensor,
    PowerSensor,
    VoltageSensor,
)
from platypush.entities.heart import HeartRateSensor
from platypush.entities.humidity import DewPointSensor, HumiditySensor
from platypush.entities.illuminance import IlluminanceSensor
from platypush.entities.motion import MotionSensor
from platypush.entities.presence import PresenceSensor
from platypush.entities.pressure import PressureSensor
from platypush.entities.sensors import BinarySensor, NumericSensor, RawSensor
from platypush.entities.steps import StepsSensor
from platypush.entities.temperature import TemperatureSensor
from platypush.entities.time import TimeDuration
from platypush.entities.weight import WeightSensor

from .._model import Protocol, ServiceClass


@dataclass
class TheengsEntity:
    """
    Utility class to store the data parsed from the Theengs library.
    """

    data: dict = field(default_factory=dict)
    properties: dict = field(default_factory=dict)
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    model_id: Optional[str] = None


# pylint: disable=too-few-public-methods
class NullSensor:
    """
    Dummy class to model sensors with null values (hence without sufficient
    information for the application to infer the type).
    """

    def __init__(self, *_, **__):
        pass


# Maps property names to transformer methods (first mapper choice).
_property_to_entity: Dict[str, Callable[[Any, Dict[str, Any]], Entity]] = {
    'activity heart rate': lambda value, _: HeartRateSensor(value=value),
    'atmospheric pressure': lambda value, conf: PressureSensor(
        value=value,
        unit=conf.get('unit'),
    ),
    'battery': lambda value, conf: Battery(
        value=value,
        unit=conf.get('unit', '%'),
        min=conf.get('min', 0),
        max=conf.get('min', 100),
    ),
    'contact': lambda value, _: ContactSensor(value=value),
    'current': lambda value, conf: CurrentSensor(
        value=value,
        unit=conf.get('unit', 'A'),
    ),
    'dew_point_sensor': lambda value, conf: DewPointSensor(
        value=value,
        unit=conf.get('unit'),
    ),
    'duration': lambda value, conf: TimeDuration(
        value=value,
        unit=conf.get('unit'),
    ),
    'energy': lambda value, conf: EnergySensor(
        value=value,
        unit=conf.get('unit', 'kWh'),
    ),
    'heart rate': lambda value, _: HeartRateSensor(value=value),
    'humidity': lambda value, conf: HumiditySensor(
        value=value,
        unit=conf.get('unit', '%'),
        min=conf.get('min', 0),
        max=conf.get('min', 100),
    ),
    'light level': lambda value, conf: IlluminanceSensor(
        value=value,
        unit=conf.get('unit'),
    ),
    'luminance': lambda value, conf: IlluminanceSensor(
        value=value,
        unit=conf.get('unit'),
    ),
    'moisture': lambda value, conf: HumiditySensor(
        value=value,
        unit=conf.get('unit'),
    ),
    'motion': lambda value, _: MotionSensor(value=value),
    'open': lambda value, _: BinarySensor(value=value),
    'power': lambda value, conf: PowerSensor(
        value=value,
        unit=conf.get('unit', 'W'),
    ),
    'presence': lambda value, _: PresenceSensor(value=value),
    'pressure': lambda value, conf: PressureSensor(
        value=value,
        unit=conf.get('unit'),
    ),
    'steps': lambda value, _: StepsSensor(value=value),
    'temperature': lambda value, conf: TemperatureSensor(
        value=value,
        unit=conf.get('unit', 'C'),
    ),
    'temperature2': lambda value, conf: TemperatureSensor(
        value=value,
        unit=conf.get('unit', 'C'),
    ),
    'temperature3': lambda value, conf: TemperatureSensor(
        value=value,
        unit=conf.get('unit', 'C'),
    ),
    'temperature4': lambda value, conf: TemperatureSensor(
        value=value,
        unit=conf.get('unit', 'C'),
    ),
    'temperature5': lambda value, conf: TemperatureSensor(
        value=value,
        unit=conf.get('unit', 'C'),
    ),
    'temperature6': lambda value, conf: TemperatureSensor(
        value=value,
        unit=conf.get('unit', 'C'),
    ),
    'temperature7': lambda value, conf: TemperatureSensor(
        value=value,
        unit=conf.get('unit', 'C'),
    ),
    'temperature8': lambda value, conf: TemperatureSensor(
        value=value,
        unit=conf.get('unit', 'C'),
    ),
    'volt': lambda value, conf: VoltageSensor(
        value=value,
        unit=conf.get('unit', 'V'),
    ),
    'voltage': lambda value, conf: VoltageSensor(
        value=value,
        unit=conf.get('unit', 'V'),
    ),
    'weight': lambda value, conf: WeightSensor(
        value=value,
        unit=conf.get('unit', 'kg'),
    ),
}

# Maps reported units to transformer methods (second mapper choice).
_unit_to_entity: Dict[str, Callable[[Any, Dict[str, Any]], Entity]] = {
    'status': lambda value, _: BinarySensor(value=value),
    'int': lambda value, _: NumericSensor(value=value),
    'float': lambda value, _: NumericSensor(value=value),
    '%': lambda value, conf: NumericSensor(
        value=value,
        unit=conf.get('unit', '%'),
        min=conf.get('min', 0),
        max=conf.get('min', 100),
    ),
}


# Maps value types to transformer methods (third mapper choice).
_value_type_to_entity: Dict[type, Callable[[Any, Dict[str, Any]], Entity]] = {
    bool: lambda value, _: BinarySensor(value=value),
    int: lambda value, _: NumericSensor(value=value),
    float: lambda value, _: NumericSensor(value=value),
    str: lambda value, _: RawSensor(value=value),
    bytes: lambda value, _: RawSensor(value=value),
    bytearray: lambda value, _: RawSensor(value=value),
}


def _parse_services(
    device: BLEDevice, data: AdvertisementData
) -> List[BluetoothService]:
    """
    :param device: The target device.
    :param data: Published beacon data.
    :return: The parsed BLE services as a list of
        :class:`platypush.entities.bluetooth.BluetoothService`.
    """
    services: List[BluetoothService] = []
    for srv in data.service_uuids or []:
        try:
            uuid = BluetoothService.to_uuid(srv)
        except (TypeError, ValueError):
            # Not a valid UUID.
            continue

        srv_cls = ServiceClass.get(uuid)
        services.append(
            BluetoothService(
                id=f'{device.address}::{uuid}',
                uuid=uuid,
                name=f'[{uuid}]' if srv_cls == ServiceClass.UNKNOWN else str(srv_cls),
                protocol=Protocol.L2CAP,
                is_ble=True,
            )
        )

    return services


def device_to_entity(device: BLEDevice, data: AdvertisementData) -> BluetoothDevice:
    """
    Convert the data received from a Bluetooth advertisement packet into a
    compatible Platypush :class:`platypush.entity.bluetooth.BluetoothDevice`
    entity, with the discovered services and characteristics exposed as children
    entities.
    """

    theengs_entity = _parse_advertisement_data(data)
    props = (device.details or {}).get('props', {})
    manufacturer = _parse_manufacturer(device, theengs_entity, data)
    parent_entity = BluetoothDevice(
        id=device.address,
        model=theengs_entity.model,
        reachable=True,
        supports_ble=True,
        supports_legacy=False,
        address=device.address,
        name=device.name or device.address,
        connected=props.get('Connected', False),
        rssi=data.rssi,
        tx_power=props.get('TxPower'),
        manufacturer=manufacturer,
        children=_parse_services(device, data),
    )

    parsed_entities = {
        # Check if we can infer an entity mapper from the property name.
        conf.get('name', name): _property_to_entity.get(
            conf.get('name'),
            # If not, check if we can infer an entity mapper from the reported unit.
            _unit_to_entity.get(
                conf.get('unit'),
                # If not, check if we can infer an entity mapper from the value type.
                _value_type_to_entity.get(
                    type(theengs_entity.data.get(name)),
                    # If not, default to a NullSensor.
                    lambda *_: NullSensor(),
                ),
            ),
        )(theengs_entity.data.get(name), conf)
        for name, conf in theengs_entity.properties.items()
    }

    for prop, entity in parsed_entities.items():
        if isinstance(entity, NullSensor):
            # Skip entities that we couldn't parse.
            continue

        entity.id = f'{parent_entity.address}::{prop}'
        entity.name = prop.title()
        parent_entity.children.append(entity)
        entity.parent = parent_entity

    return parent_entity


def _parse_manufacturer(
    device: BLEDevice, entity: TheengsEntity, data: AdvertisementData
) -> Optional[str]:
    """
    :param device: The target device.
    :param entity: The entity that maps the received beacon data.
    :param data:
    :return: The parsed manufacturer name.
    """

    # If the manufacturer has already been parsed, return it.
    if entity.manufacturer:
        return entity.manufacturer

    # Otherwise, infer it from the first three bytes of the MAC address.
    manufacturer = oui.get(':'.join(device.address.split(':')[:3]).upper())
    if manufacturer:
        return manufacturer

    # Otherwise, infer it from the reported manufacturer_data.
    for key in data.manufacturer_data:
        manufacturer = company.get(key)
        if manufacturer:
            return manufacturer

    # Otherwise, we couldn't parse the manufacturer.
    return None


def _parse_advertisement_data(data: AdvertisementData) -> TheengsEntity:
    """
    :param data: The data received from a Bluetooth advertisement packet.
    :return: A :class:`platypush.entity.bluetooth.TheengsEntity` instance that
        maps the parsed attributes.
    """

    entity_args, properties, manufacturer, model, model_id = ({}, {}, None, None, None)

    if data.service_data:
        parsed_data = list(data.service_data.keys())[0]
        # TheengsDecoder only accepts 16 bit uuid's, this converts the 128 bit uuid to 16 bit.
        entity_args['servicedatauuid'] = parsed_data[4:8]
        parsed_data = str(list(data.service_data.values())[0].hex())
        entity_args['servicedata'] = parsed_data

    if data.manufacturer_data:
        parsed_data = str(
            struct.pack('<H', list(data.manufacturer_data.keys())[0]).hex()
        )
        parsed_data += str(list(data.manufacturer_data.values())[0].hex())
        entity_args['manufacturerdata'] = parsed_data

    if data.local_name:
        entity_args['name'] = data.local_name

    if entity_args:
        encoded_ret = decodeBLE(json.dumps(entity_args))

        if encoded_ret:
            entity_args = json.loads(encoded_ret)

            if entity_args.get('model_id'):
                properties = json.loads(getProperties(entity_args['model_id'])).get(
                    'properties', {}
                )
                model = getAttribute(entity_args['model_id'], 'model')

        model_id = entity_args.pop('model_id', None)

    return TheengsEntity(
        data=entity_args,
        properties=properties,
        manufacturer=manufacturer,
        model=model,
        model_id=model_id,
    )
