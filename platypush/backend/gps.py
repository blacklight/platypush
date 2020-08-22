import threading
import time

from platypush.backend import Backend
from platypush.message.event.gps import GPSVersionEvent, GPSDeviceEvent, GPSUpdateEvent


class GpsBackend(Backend):
    """
    This backend can interact with a GPS device and listen for events.

    Triggers:

        * :class:`platypush.message.event.gps.GPSVersionEvent` when a GPS device advertises its version data
        * :class:`platypush.message.event.gps.GPSDeviceEvent` when a GPS device is connected or updated
        * :class:`platypush.message.event.gps.GPSUpdateEvent` when a GPS device has new data

    Requires:

        * **gps** (``pip install gps``)
        * **gpsd** daemon running (``apt-get install gpsd`` or ``pacman -S gpsd`` depending on your distro)

    Once installed gpsd you need to run it and associate it to your device. Example if your GPS device communicates
    over USB and is available on /dev/ttyUSB0::

        [sudo] gpsd /dev/ttyUSB0 -F /var/run/gpsd.sock

    The best option is probably to run gpsd at startup as a systemd service.
    """

    _fail_sleep_time = 5.0
    _lat_lng_tolerance = 1e-5
    _alt_tolerance = 0.5

    def __init__(self, gpsd_server='localhost', gpsd_port=2947, **kwargs):
        """
        :param gpsd_server: gpsd daemon server name/address (default: localhost)
        :type gpsd_server: str
        :param gpsd_port: Port of the gpsd daemon (default: 2947)
        :type gpsd_port: int or str
        """
        super().__init__(**kwargs)

        self.gpsd_server = gpsd_server
        self.gpsd_port = gpsd_port
        self._session = None
        self._session_lock = threading.RLock()
        self._devices = {}

    def _get_session(self):
        import gps

        with self._session_lock:
            if not self._session:
                self._session = gps.gps(host=self.gpsd_server, port=self.gpsd_port, reconnect=True)
                self._session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)

        return self._session

    def _gps_report_to_event(self, report):
        if report.get('class').lower() == 'version':
            return GPSVersionEvent(release=report.get('release'),
                                   rev=report.get('rev'),
                                   proto_major=report.get('proto_major'),
                                   proto_minor=report.get('proto_minor'))
        if report.get('class').lower() == 'devices':
            for device in report.get('devices', []):
                if device.get('path') not in self._devices or device != self._devices.get('path'):
                    # noinspection DuplicatedCode
                    self._devices[device.get('path')] = device
                    return GPSDeviceEvent(path=device.get('path'), activated=device.get('activated'),
                                          native=device.get('native'), bps=device.get('bps'),
                                          parity=device.get('parity'), stopbits=device.get('stopbits'),
                                          cycle=device.get('cycle'), driver=device.get('driver'))
        if report.get('class').lower() == 'device':
            # noinspection DuplicatedCode
            self._devices[report.get('path')] = report
            return GPSDeviceEvent(path=report.get('path'), activated=report.get('activated'),
                                  native=report.get('native'), bps=report.get('bps'),
                                  parity=report.get('parity'), stopbits=report.get('stopbits'),
                                  cycle=report.get('cycle'), driver=report.get('driver'))
        if report.get('class').lower() == 'tpv':
            return GPSUpdateEvent(device=report.get('device'), latitude=report.get('lat'), longitude=report.get('lon'),
                                  altitude=report.get('alt'), mode=report.get('mode'), epv=report.get('epv'),
                                  eph=report.get('eph'), sep=report.get('sep'))

    def run(self):
        super().run()
        self.logger.info('Initialized GPS backend on {}:{}'.format(self.gpsd_server, self.gpsd_port))
        last_event = None

        while not self.should_stop():
            try:
                session = self._get_session()
                report = session.next()
                event = self._gps_report_to_event(report)
                if event and (last_event is None or
                              abs((last_event.args.get('latitude') or 0) - (event.args.get('latitude') or 0)) >= self._lat_lng_tolerance or
                              abs((last_event.args.get('longitude') or 0) - (event.args.get('longitude') or 0)) >= self._lat_lng_tolerance or
                              abs((last_event.args.get('altitude') or 0) - (event.args.get('altitude') or 0)) >= self._alt_tolerance):
                    self.bus.post(event)
                    last_event = event
            except Exception as e:
                if isinstance(e, StopIteration):
                    self.logger.warning('GPS service connection lost, check that gpsd is running')
                else:
                    self.logger.exception(e)

                self._session = None
                time.sleep(self._fail_sleep_time)


# vim:sw=4:ts=4:et:
