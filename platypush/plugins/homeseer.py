
from platypush.plugins import Plugin, action


class HomeseerPlugin(Plugin):
    """
    This plugin allows you interact with an existing HomeSeer setup,
    query and control connected devices.

    Requires:

        * **pyhomeseer** (``pip install git+https://github.com/legrego/PyHomeSeer``)
    """

    def __init__(self, host, username=None, password=None, *args, **kwargs):
        """
        :param host: IP or hostname of your HomeSeer hub
        :type host: str

        :param username: HomeSeer username
        :type username: str

        :param password: HomeSeer password
        :type password: str
        """

        super().__init__(*args, **kwargs)

        self.host = host
        self.username = username
        self.password = password
        self._client = None

    def _get_client(self):
        from pyhomeseer.homeseer_client import HomeSeerClient

        if not self._client:
            self._client = HomeSeerClient(host=self.host,
                                          username=self.username,
                                          password=self.password)

        return self._client


    @action
    def query_devices(self, ref=None, location=None):
        """
        Get a list of devices connected to HomeSeer with their status

        :param ref: Device reference. If not set, all the devices will be queried
        :type ref: int

        :param location: Device location. If not set, all the devices will be queried
        :type location: str
        """

        client = self._get_client()

        if ref is not None:
            devices = client.get_devices(ref=ref)
        elif location is not None:
            devices = client.get_devices(location=location)
        else:
            devices = client.get_devices()

        return [
            {
                attr: getattr(dev, attr)
                for attr in ['ref','name','location','value','status']
            }
            for dev in devices
        ]


    @action
    def control(self, ref, value=None, label=None):
        """
        Control a HomeSeer connected device.

        :param ref: Device reference
        :type ref: int

        :param value: If set, then control the device with this specific int value
        :type value: int

        :param label: If set, then control the device with this specific label
            (e.g. 'On' or 'Off')
        :type label: str
        """

        if value is None and label is None:
            raise RuntimeError('Please specify either value or label')

        client = self._get_client()

        if value is not None:
            return client.control(ref=ref, value=value)
        return client.control(ref=ref, label=label)


# vim:sw=4:ts=4:et:
