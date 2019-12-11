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
    Example services response output::

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


# vim:sw=4:ts=4:et:
