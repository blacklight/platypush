import dateutil.parser
import importlib

from abc import ABCMeta, abstractmethod

from platypush.plugins import Plugin, action


class CalendarInterface:
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_upcoming_events(self, max_results=10):
        raise NotImplementedError()


class CalendarPlugin(Plugin, CalendarInterface):
    """
    The CalendarPlugin allows you to keep track of multiple calendars (Google or
    iCal URLs) and get joined events from all of them.
    """

    def __init__(self, calendars=None, *args, **kwargs):
        """
        :param calendars: List of calendars to be queried. Supported types so far: Google Calendar and iCal URLs.
        :type calendars: list

        Example format::

            calendars = [
                {
                    "type": "platypush.plugins.google.calendar.GoogleCalendarPlugin"
                },

                {
                    "type": "platypush.plugins.calendar.ical.IcalCalendarPlugin",
                    "url": "https://www.facebook.com/ical/u.php?uid=USER_ID&key=FB_KEY"
                },

                ...
            ]
        """

        super().__init__(*args, **kwargs)

        if calendars is None:
            calendars = []
        self.calendars = []

        for calendar in calendars:
            if 'type' not in calendar:
                self.logger.warning(
                    "Invalid calendar with no type specified: {}".format(calendar)
                )
                continue

            cal_type = calendar.pop('type')
            module_name = '.'.join(cal_type.split('.')[:-1])
            class_name = cal_type.split('.')[-1]
            module = importlib.import_module(module_name)
            self.calendars.append(getattr(module, class_name)(**calendar))

    @action
    def get_upcoming_events(self, max_results=10):
        """
        Get a list of upcoming events merging all the available calendars.

        :param max_results: Maximum number of results to be returned (default: 10)
        :type max_results: int

        :returns: platypush.message.Response -- Response object with the list of
            events in the Google calendar API format.

        Example::

            output = [
                {
                    "id": "123456abcdef",
                    "kind": "calendar#event",
                    "status": "confirmed",
                    "htmlLink": "...",
                    "created": "2018-06-01T01:23:45.000Z",
                    "updated": "2018-06-01T01:23:45.000Z",
                    "creator": {
                        "email": "...",
                        "displayName": "...",
                        "self": true
                    },
                    "organizer" {
                        "email": "...",
                        "displayName": "...",
                        "self": true
                    },
                    "start": {
                        "dateTime": "2018-06-02T10:00:00.000Z",
                    },
                    "end": {
                        "dateTime": "2018-06-02T12:00:00.000Z",
                    },
                },
                ...
            ]
        """

        events = []

        for calendar in self.calendars:
            try:
                cal_events = calendar.get_upcoming_events().output or []
                events.extend(cal_events)
            except Exception as e:
                self.logger.warning('Could not retrieve events: {}'.format(str(e)))

        events = sorted(
            events,
            key=lambda event: dateutil.parser.parse(
                event['start']['dateTime']
                if 'dateTime' in event['start']
                else event['start']['date'] + 'T00:00:00+00:00'
            ),
        )[:max_results]

        return events


# vim:sw=4:ts=4:et:
