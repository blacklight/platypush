from typing import Dict, Any

from platypush.message.event import Event


class ZigbeeMqttEvent(Event):
    pass


class ZigbeeMqttOnlineEvent(ZigbeeMqttEvent):
    """
    Triggered when a zigbee2mqtt service goes online.
    """
    def __init__(self, host: str, port: int, *args, **kwargs):
        super().__init__(*args, host=host, port=port, **kwargs)


class ZigbeeMqttOfflineEvent(ZigbeeMqttEvent):
    """
    Triggered when a zigbee2mqtt service goes offline.
    """
    def __init__(self, host: str, port: int, *args, **kwargs):
        super().__init__(*args, host=host, port=port, **kwargs)


class ZigbeeMqttDevicePropertySetEvent(ZigbeeMqttEvent):
    """
    Triggered when a the properties of a Zigbee connected devices (state, brightness, alert etc.) change.
    """
    def __init__(self, host: str, port: int, device: str, properties: Dict[str, Any], *args, **kwargs):
        super().__init__(*args, host=host, port=port, device=device, properties=properties, **kwargs)


class ZigbeeMqttDevicePairingEvent(ZigbeeMqttEvent):
    """
    Triggered when a device is pairing to the network.
    """
    def __init__(self, host: str, port: int, device=None, *args, **kwargs):
        super().__init__(*args, host=host, port=port, device=device, **kwargs)


class ZigbeeMqttDeviceConnectedEvent(ZigbeeMqttEvent):
    """
    Triggered when a device connects to the network.
    """
    def __init__(self, host: str, port: int, device=None, *args, **kwargs):
        super().__init__(*args, host=host, port=port, device=device, **kwargs)


class ZigbeeMqttDeviceBannedEvent(ZigbeeMqttEvent):
    """
    Triggered when a device is banned from the network.
    """
    def __init__(self, host: str, port: int, device=None, *args, **kwargs):
        super().__init__(*args, host=host, port=port, device=device, **kwargs)


class ZigbeeMqttDeviceRemovedEvent(ZigbeeMqttEvent):
    """
    Triggered when a device is removed from the network.
    """
    def __init__(self, host: str, port: int, device=None, force=False, *args, **kwargs):
        super().__init__(*args, host=host, port=port, device=device, force=force, **kwargs)


class ZigbeeMqttDeviceRemovedFailedEvent(ZigbeeMqttEvent):
    """
    Triggered when the removal of a device from the network failed.
    """
    def __init__(self, host: str, port: int, device=None, *args, **kwargs):
        super().__init__(*args, host=host, port=port, device=device, **kwargs)


class ZigbeeMqttDeviceWhitelistedEvent(ZigbeeMqttEvent):
    """
    Triggered when a device is whitelisted on the network.
    """
    def __init__(self, host: str, port: int, device=None, *args, **kwargs):
        super().__init__(*args, host=host, port=port, device=device, **kwargs)


class ZigbeeMqttDeviceRenamedEvent(ZigbeeMqttEvent):
    """
    Triggered when a device is renamed on the network.
    """
    def __init__(self, host: str, port: int, device=None, *args, **kwargs):
        super().__init__(*args, host=host, port=port, device=device, **kwargs)


class ZigbeeMqttDeviceBindEvent(ZigbeeMqttEvent):
    """
    Triggered when a device bind occurs on the network.
    """
    def __init__(self, host: str, port: int, device=None, *args, **kwargs):
        super().__init__(*args, host=host, port=port, device=device, **kwargs)


class ZigbeeMqttDeviceUnbindEvent(ZigbeeMqttEvent):
    """
    Triggered when a device bind occurs on the network.
    """
    def __init__(self, host: str, port: int, device=None, *args, **kwargs):
        super().__init__(*args, host=host, port=port, device=device, **kwargs)


class ZigbeeMqttGroupAddedEvent(ZigbeeMqttEvent):
    """
    Triggered when a group is added.
    """
    def __init__(self, host: str, port: int, group=None, *args, **kwargs):
        super().__init__(*args, host=host, port=port, group=group, **kwargs)


class ZigbeeMqttGroupAddedFailedEvent(ZigbeeMqttEvent):
    """
    Triggered when a request to add a group fails.
    """
    def __init__(self, host: str, port: int, group=None, *args, **kwargs):
        super().__init__(*args, host=host, port=port, group=group, **kwargs)


class ZigbeeMqttGroupRemovedEvent(ZigbeeMqttEvent):
    """
    Triggered when a group is removed.
    """
    def __init__(self, host: str, port: int, group=None, *args, **kwargs):
        super().__init__(*args, host=host, port=port, group=group, **kwargs)


class ZigbeeMqttGroupRemovedFailedEvent(ZigbeeMqttEvent):
    """
    Triggered when a request to remove a group fails.
    """
    def __init__(self, host: str, port: int, group=None, *args, **kwargs):
        super().__init__(*args, host=host, port=port, group=group, **kwargs)


class ZigbeeMqttGroupRemoveAllEvent(ZigbeeMqttEvent):
    """
    Triggered when all the devices are removed from a group.
    """
    def __init__(self, host: str, port: int, group=None, *args, **kwargs):
        super().__init__(*args, host=host, port=port, group=group, **kwargs)


class ZigbeeMqttGroupRemoveAllFailedEvent(ZigbeeMqttEvent):
    """
    Triggered when a request to remove all the devices from a group fails.
    """
    def __init__(self, host: str, port: int, group=None, *args, **kwargs):
        super().__init__(*args, host=host, port=port, group=group, **kwargs)


class ZigbeeMqttErrorEvent(ZigbeeMqttEvent):
    """
    Triggered when an error happens on the zigbee2mqtt service.
    """
    def __init__(self, host: str, port: int, error=None, *args, **kwargs):
        super().__init__(*args, host=host, port=port, error=error, **kwargs)


# vim:sw=4:ts=4:et:
