from platypush.message.response import Response


class BluetoothResponse(Response):
    pass


class BluetoothScanResponse(BluetoothResponse):
    def __init__(self, devices, *args, **kwargs):
        if isinstance(devices, list):
            self.devices = [
                {
                    'addr': dev[0],
                    'name': dev[1] if len(dev) > 1 else None,
                    'class': hex(dev[2]) if len(dev) > 2 else None,
                }
                for dev in devices
            ]
        elif isinstance(devices, dict):
            self.devices = [
                {
                    'addr': addr,
                    'name': name or None,
                    'class': 'BLE',
                }
                for addr, name in devices.items()
            ]
        else:
            raise ValueError('devices must be either a list of tuples or a dict')

        super().__init__(output=self.devices, *args, **kwargs)


class BluetoothLookupNameResponse(BluetoothResponse):
    def __init__(self, addr: str, name: str, *args, **kwargs):
        self.addr = addr
        self.name = name
        super().__init__(output={
            'addr': self.addr,
            'name': self.name
        }, *args, **kwargs)


class BluetoothLookupServiceResponse(BluetoothResponse):
    """
    Example services response output:

      .. code-block:: json

        [
          {
            "service-classes": [
              "1801"
            ],
            "profiles": [],
            "name": "Service name #1",
            "description": null,
            "provider": null,
            "service-id": null,
            "protocol": "L2CAP",
            "port": 31,
            "host": "00:11:22:33:44:55"
          },
          {
            "service-classes": [
              "1800"
            ],
            "profiles": [],
            "name": "Service name #2",
            "description": null,
            "provider": null,
            "service-id": null,
            "protocol": "L2CAP",
            "port": 31,
            "host": "00:11:22:33:44:56"
          },
          {
            "service-classes": [
              "1112",
              "1203"
            ],
            "profiles": [
              [
                "1108",
                258
              ]
            ],
            "name": "Headset Gateway",
            "description": null,
            "provider": null,
            "service-id": null,
            "protocol": "RFCOMM",
            "port": 2,
            "host": "00:11:22:33:44:57"
          }
        ]

    """
    def __init__(self, services: list, *args, **kwargs):
        self.services = services
        super().__init__(output=self.services, *args, **kwargs)


class BluetoothDiscoverPrimaryResponse(BluetoothResponse):
    """
    Example services response output:

      .. code-block:: json

        [
          {
            "uuid": "00001800-0000-1000-8000-00805f9b34fb",
            "start": 1,
            "end": 7
          },
          {
            "uuid": "00001801-0000-1000-8000-00805f9b34fb",
            "start": 8,
            "end": 8
          },
          {
            "uuid": "0000fee7-0000-1000-8000-00805f9b34fb",
            "start": 9,
            "end": 16
          },
          {
            "uuid": "cba20d00-224d-11e6-9fb8-0002a5d5c51b",
            "start": 17,
            "end": 65535
          }
        ]

    """
    def __init__(self, services: list, *args, **kwargs):
        self.services = services
        super().__init__(output=self.services, *args, **kwargs)


class BluetoothDiscoverCharacteristicsResponse(BluetoothResponse):
    """
    Example services response output:

      .. code-block:: json

        [
          {
            "uuid": "00002a00-0000-1000-8000-00805f9b34fb",
            "handle": 2,
            "properties": 10,
            "value_handle": 3
          },
          {
            "uuid": "00002a01-0000-1000-8000-00805f9b34fb",
            "handle": 4,
            "properties": 2,
            "value_handle": 5
          },
          {
            "uuid": "00002a04-0000-1000-8000-00805f9b34fb",
            "handle": 6,
            "properties": 2,
            "value_handle": 7
          },
          {
            "uuid": "0000fec8-0000-1000-8000-00805f9b34fb",
            "handle": 10,
            "properties": 32,
            "value_handle": 11
          },
          {
            "uuid": "0000fec7-0000-1000-8000-00805f9b34fb",
            "handle": 13,
            "properties": 8,
            "value_handle": 14
          },
          {
            "uuid": "0000fec9-0000-1000-8000-00805f9b34fb",
            "handle": 15,
            "properties": 2,
            "value_handle": 16
          },
          {
            "uuid": "cba20003-224d-11e6-9fb8-0002a5d5c51b",
            "handle": 18,
            "properties": 16,
            "value_handle": 19
          },
          {
            "uuid": "cba20002-224d-11e6-9fb8-0002a5d5c51b",
            "handle": 21,
            "properties": 12,
            "value_handle": 22
          }
        ]

    """
    def __init__(self, characteristics: list, *args, **kwargs):
        self.characteristics = characteristics
        super().__init__(output=self.characteristics, *args, **kwargs)


# vim:sw=4:ts=4:et:
