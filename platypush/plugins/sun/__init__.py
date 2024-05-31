import datetime
from typing import Dict, Optional

import requests
from dateutil.tz import gettz

from platypush.message.event.sun import SunriseEvent, SunsetEvent
from platypush.plugins import RunnablePlugin, action
from platypush.schemas.sun import SunEventsSchema
from platypush.utils import utcnow


class SunPlugin(RunnablePlugin):
    """
    Plugin to get sunset/sunrise events and info for a certain location.
    """

    _base_url = 'https://api.sunrise-sunset.org/json'
    _schema = SunEventsSchema()
    _attr_to_event_class = {
        'sunrise': SunriseEvent,
        'sunset': SunsetEvent,
    }

    def __init__(self, latitude: float, longitude: float, **kwargs):
        """
        :param latitude: Default latitude.
        :param longitude: Default longitude.
        """
        super().__init__(**kwargs)
        self.latitude = latitude
        self.longitude = longitude

    def main(self):
        while not self.should_stop():
            next_events = self._get_events()
            next_event = next(
                iter(
                    sorted(
                        [
                            event_class(
                                latitude=self.latitude,
                                longitude=self.longitude,
                                time=next_events[attr],
                            )
                            for attr, event_class in self._attr_to_event_class.items()
                            if next_events.get(attr)
                        ],
                        key=lambda t: t.time,
                    )
                ),
                None,
            )

            assert next_event is not None, 'No next event found'
            wait_secs = max(
                0, (next_event.time - datetime.datetime.now(tz=gettz())).seconds
            )
            self.wait_stop(wait_secs)

            if not self.should_stop():
                self._bus.post(next_event)
                self.wait_stop(2)

    @staticmethod
    def _convert_time(t: str) -> datetime.datetime:
        now = utcnow().replace(microsecond=0)
        dt = datetime.datetime.strptime(
            f'{now.year}-{now.month:02d}-{now.day:02d} {t}',
            '%Y-%m-%d %I:%M:%S %p',
        ).replace(tzinfo=datetime.timezone.utc)

        if dt < now:
            dt += datetime.timedelta(days=1)
        return dt

    def _get_events(
        self, latitude: Optional[float] = None, longitude: Optional[float] = None
    ) -> Dict[str, datetime.datetime]:
        response = (
            requests.get(
                self._base_url,
                timeout=10,
                params={
                    'lat': latitude or self.latitude,
                    'lng': longitude or self.longitude,
                },
            )
            .json()
            .get('results', {})
        )

        return {
            attr: self._convert_time(t)
            for attr, t in response.items()
            if attr in self._schema.declared_fields
        }

    @action
    def get_events(
        self, latitude: Optional[float] = None, longitude: Optional[float] = None
    ) -> dict:
        """
        Return the next sun events.

        :param latitude: Override the default latitude.
        :param longitude: Override the default longitude.
        :return: .. schema:: sun.SunEventsSchema
        """
        schema = SunEventsSchema()
        return dict(
            schema.dump(self._get_events(latitude=latitude, longitude=longitude))
        )
