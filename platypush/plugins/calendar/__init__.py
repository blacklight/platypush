import dateutil.parser
import importlib
import logging

from abc import ABCMeta, abstractmethod

from platypush.plugins import Plugin
from platypush.message.response import Response


class CalendarInterface:
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_upcoming_events(self, max_results=10):
        raise NotImplementedError()


class CalendarPlugin(Plugin, CalendarInterface):
    """
    The CalendarPlugin will allow you to keep track of multiple calendars
    (Google or iCal URLs) and get joined events from all of them
    """

    def __init__(self, calendars=[], *args, **kwargs):
        """
        Example calendars format:

        ```
            [
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
        self.calendars = []

        for calendar in calendars:
            if 'type' not in calendar:
                logging.warning("Invalid calendar with no type specified: {}".format(calendar))
                continue

            cal_type = calendar.pop('type')
            module_name = '.'.join(cal_type.split('.')[:-1])
            class_name = cal_type.split('.')[-1]
            module = importlib.import_module(module_name)
            self.calendars.append(getattr(module, class_name)(**calendar))


    def get_upcoming_events(self, max_results=10):
        events = []

        for calendar in self.calendars:
            events.extend(calendar.get_upcoming_events().output)

        events = sorted(events, key=lambda event:
                        dateutil.parser.parse(event['start']['dateTime']))[:max_results]

        return Response(output=events)


# vim:sw=4:ts=4:et:

