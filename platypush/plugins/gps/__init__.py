import threading
from contextlib import contextmanager
from dataclasses import asdict
from datetime import datetime

from platypush.plugins import RunnablePlugin, action
from platypush.message.event.gps import (
    GPSDeviceEvent,
    GPSDisabledEvent,
    GPSEnabledEvent,
    GPSLocationUpdateEvent,
)
from platypush.schemas.gps import GpsDeviceSchema, GpsStatusSchema

from ._model import DeviceMode, GpsDevice, GpsStatus


class GpsPlugin(RunnablePlugin):
    """
    This plugin can interact with a GPS device compatible with `gpsd
    <https://gpsd.io/>`_ and emit events when the location changes.

    It requires ``gpsd`` to run on a system with a compatible GPS device
    connected - most of the off-the-shelf GPS devices over USB or serial
    interfaces should tick the box.

    For example, if your GPS device communicates over USB and is available on
    /dev/ttyUSB0, you can start the gpsd daemon with the following command
    before starting Platypush::

        [sudo] gpsd /dev/ttyUSB0 [-S 2947]

    It will expose GPS events over the port ``2947`` by default, and you can
    subscribe to them through this plugin.
    """

    _default_gpsd_port = 2947
    _default_poll_interval = 5.0
    _lat_lng_tolerance = 1e-5
    _alt_tolerance = 0.5

    def __init__(
        self,
        gpsd_server: str = 'localhost',
        gpsd_port: int = _default_gpsd_port,
        poll_interval: float = _default_poll_interval,
        enable_on_start: bool = True,
        **kwargs,
    ):
        """
        :param gpsd_server: gpsd daemon server name/address (default: localhost).
        :param gpsd_port: Port of the gpsd daemon (default: 2947).
        :param poll_interval: How long to wait before polling the GPS device
            again in case of error (default: 5 seconds).
        :param enable_on_start: If True, the GPS polling will be enabled when the
            plugin starts (default: True). Otherwise, it'll have to be enabled by
            calling the :meth:`.enable` action.
        """
        super().__init__(poll_interval=poll_interval, **kwargs)

        self.gpsd_server = gpsd_server
        self.gpsd_port = gpsd_port
        self._enable_on_start = enable_on_start
        self._session = None
        self._session_lock = threading.RLock()
        self._status = GpsStatus()

    @contextmanager
    def _get_session(self):
        import gps

        with self._session_lock:
            if not self._session:
                self._session = gps.gps(
                    host=self.gpsd_server, port=self.gpsd_port, reconnect=True  # type: ignore
                )

        yield self._session

        with self._session_lock:
            try:
                self.disable()
            except Exception as e:
                self.logger.warning('Error disabling GPSD watch: %s', e)

            self._session.close()
            self._session = None

    def _update_device(self, device: dict):
        path = device.get('path')
        if not path:
            return

        cur_dev = self._status.devices.get(path)
        new_dev = GpsDevice(**GpsDeviceSchema().load(device))  # type: ignore
        if cur_dev and asdict(cur_dev) == asdict(new_dev):
            return

        self._status.devices[path] = new_dev
        self._bus.post(GPSDeviceEvent(**asdict(new_dev)))

    def _handle_location_update(self, report: dict):
        dev, lat, long, alt, mode, t = (
            report.get('device'),
            report.get('lat'),
            report.get('lon'),
            report.get('alt'),
            report.get('mode'),
            report.get('time'),
        )

        if not (dev and lat and long and mode):
            return

        dev_mode = DeviceMode(mode)
        self._status.timestamp = datetime.fromisoformat(t) if t else None
        self._status.devices[dev].mode = dev_mode

        if not (
            abs((self._status.latitude or 0) - lat) >= self._lat_lng_tolerance
            or abs((self._status.longitude or 0) - long) >= self._lat_lng_tolerance
            or abs((self._status.altitude or 0) - (alt or 0)) >= self._alt_tolerance
        ):
            return

        event = GPSLocationUpdateEvent(
            device=dev,
            latitude=lat,
            longitude=long,
            altitude=alt,
            mode=dev_mode.name,
        )

        self._status.latitude = lat
        self._status.longitude = long
        self._status.altitude = alt
        self._bus.post(event)

    def _handle_report(self, report: dict):
        cls = report['class'].lower()
        if cls == 'version':
            self.logger.info('Received GPSD version event: %s', dict(report))
            return

        if cls == 'watch':
            evt_type = GPSEnabledEvent if report.get('enable') else GPSDisabledEvent
            self._bus.post(evt_type())
            return

        if cls == 'devices':
            for device in report.get('devices', []):
                self._update_device(device)
            return

        if cls == 'device':
            self._update_device(report)
            return

        if cls == 'tpv':
            self._handle_location_update(report)

    @action
    def enable(self):
        """
        Enable the GPS polling.
        """
        import gps

        assert self._session, 'GPSD session not initialized'
        self._session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)

    @action
    def disable(self):
        """
        Disable the GPS polling.
        """
        import gps

        assert self._session, 'GPSD session not initialized'
        self._session.stream(gps.WATCH_DISABLE)

    @action
    def status(self):
        """
        :returns: The current GPS status:

            .. schema:: gps.GpsStatusSchema

        """
        return GpsStatusSchema().dump(self._status)

    def main(self):
        while not self.should_stop():
            first_run = True

            try:
                with self._get_session() as session:
                    if first_run and self._enable_on_start:
                        self.enable()
                        first_run = False

                    while not self.should_stop():
                        report: dict = session.next()  # type: ignore
                        self._handle_report(report)
            except Exception as e:
                if isinstance(e, StopIteration):
                    self.logger.warning(
                        'GPS service connection lost, check that gpsd is running'
                    )
                else:
                    self.logger.exception(e)

                self.wait_stop(self.poll_interval)


# vim:sw=4:ts=4:et:
