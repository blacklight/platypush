"""
.. moduleauthor:: Fabio Manganiello <blacklight86@gmail.com>
"""

import datetime
import requests
from typing import Optional

from platypush.plugins import Plugin, action
from platypush.plugins.calendar import CalendarInterface


class CalendarIcalPlugin(Plugin, CalendarInterface):
    """
    iCal calendars plugin. Interact with remote calendars in iCal format.

    Requires:

        * **icalendar** (``pip install icalendar``)

    """

    def __init__(self, url, *args, **kwargs):
        """
        :param url: iCal URL to parse
        :type url: str
        """
        super().__init__(*args, **kwargs)
        self.url = url

    @staticmethod
    def _convert_timestamp(event, attribute: str) -> Optional[str]:
        t = event.get(attribute)
        if not t:
            return

        if type(t.dt) == datetime.date:
            return (
                datetime.datetime(
                    t.dt.year, t.dt.month, t.dt.day, tzinfo=datetime.timezone.utc
                ).isoformat()
            )

        return (
                datetime.datetime.utcfromtimestamp(t.dt.timestamp())
                .replace(tzinfo=datetime.timezone.utc).isoformat()
        )

    @classmethod
    def _translate_event(cls, event):
        return {
            'id': str(event.get('uid')) if event.get('uid') else None,
            'kind': 'calendar#event',
            'summary': str(event.get('summary')) if event.get('summary') else None,
            'description': str(event.get('description')) if event.get('description') else None,
            'status': str(event.get('status')).lower() if event.get('status') else None,
            'responseStatus': str(event.get('partstat')).lower() if event.get('partstat') else None,
            'location': str(event.get('location')) if event.get('location') else None,
            'htmlLink': str(event.get('url')) if event.get('url') else None,
            'organizer': {
                'email': str(event.get('organizer')).replace('MAILTO:', ''),
                'displayName': event.get('organizer').params.get('cn')
            } if event.get('organizer') else None,

            'created': cls._convert_timestamp(event, 'created'),
            'updated': cls._convert_timestamp(event, 'last-modified'),
            'start': {
                'dateTime': cls._convert_timestamp(event, 'dtstart'),
                'timeZone': 'UTC',
            },

            'end': {
                'dateTime': cls._convert_timestamp(event, 'dtend'),
                'timeZone': 'UTC',
            },
        }

    @action
    def get_upcoming_events(self, max_results=10, only_participating=True):
        """
        Get the upcoming events. See
        :func:`~platypush.plugins.calendar.CalendarPlugin.get_upcoming_events`.
        """

        from icalendar import Calendar

        events = []
        response = requests.get(self.url)
        assert response.ok, \
            "HTTP error while getting events from {}: {}".format(self.url, response.text)

        calendar = Calendar.from_ical(response.text)
        for event in calendar.walk():
            if event.name != 'VEVENT':
                continue  # Not an event

            event = self._translate_event(event)

            if (
                    event['status'] != 'cancelled'
                    and event['end'].get('dateTime')
                    and event['end']['dateTime'] >= datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
                    and (
                    (only_participating
                     and event.get('responseStatus') in [None, 'accepted', 'tentative'])
                    or not only_participating)
            ):
                events.append(event)

        return events

# vim:sw=4:ts=4:et:
