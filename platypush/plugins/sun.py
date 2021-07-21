import datetime
import time
from typing import Optional

import requests
from dateutil.tz import gettz, tzutc

from platypush.message.event.sun import SunriseEvent, SunsetEvent
from platypush.plugins import RunnablePlugin, action
from platypush.schemas.sun import SunEventsSchema


class SunPlugin(RunnablePlugin):
    """
    Plugin to get sunset/sunrise events and info for a certain location.

    Triggers:

        * :class:`platypush.message.event.sun.SunriseEvent` on sunrise.
        * :class:`platypush.message.event.sun.SunsetEvent` on sunset.

    """
    _base_url = 'https://api.sunrise-sunset.org/json'
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
            # noinspection PyUnresolvedReferences
            next_events = self.get_events().output
            next_events = sorted([
                event_class(latitude=self.latitude, longitude=self.longitude, time=next_events[attr])
                for attr, event_class in self._attr_to_event_class.items()
                if next_events.get(attr)
            ], key=lambda t: t.time)

            for event in next_events:
                # noinspection PyTypeChecker
                dt = datetime.datetime.fromisoformat(event.time)
                while (not self.should_stop()) and (dt > datetime.datetime.now(tz=gettz())):
                    time.sleep(1)

                if dt <= datetime.datetime.now(tz=gettz()):
                    self.bus.post(event)

    @staticmethod
    def _convert_time(t: str) -> datetime.datetime:
        now = datetime.datetime.now().replace(tzinfo=gettz())  # lgtm [py/call-to-non-callable]
        dt = datetime.datetime.strptime(t, '%H:%M:%S %p')
        dt = datetime.datetime(year=now.year, month=now.month, day=now.day,
                               hour=dt.hour, minute=dt.minute, second=dt.second, tzinfo=tzutc())

        if dt < now:
            dt += datetime.timedelta(days=1)
        return datetime.datetime.fromtimestamp(dt.timestamp(), tz=gettz())

    @action
    def get_events(self, latitude: Optional[float] = None, longitude: Optional[float] = None) -> dict:
        """
        Return the next sun events.

        :param latitude: Default latitude override.
        :param longitude: Default longitude override.
        :return: .. schema:: sun.SunEventsSchema
        """
        response = requests.get(self._base_url, params={
            'lat': latitude or self.latitude,
            'lng': longitude or self.longitude,
        }).json().get('results', {})

        schema = SunEventsSchema()
        return schema.dump({
            attr: self._convert_time(t)
            for attr, t in response.items()
            if attr in schema.declared_fields.keys()
        })
