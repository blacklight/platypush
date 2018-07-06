"""
.. moduleauthor:: Fabio Manganiello <blacklight86@gmail.com>
"""

import base64
import datetime
import httplib2
import os

from apiclient import discovery

from platypush.plugins import action
from platypush.plugins.google import GooglePlugin
from platypush.plugins.calendar import CalendarInterface


class GoogleCalendarPlugin(GooglePlugin, CalendarInterface):
    """
    Google calendar plugin
    """

    scopes = ['https://www.googleapis.com/auth/calendar.readonly']

    def __init__(self, *args, **kwargs):
        super().__init__(scopes=self.scopes, *args, **kwargs)


    @action
    def get_upcoming_events(self, max_results=10):
        """
        Get the upcoming events. See
        :func:`~platypush.plugins.calendar.CalendarPlugin.get_upcoming_events`.
        """

        now = datetime.datetime.utcnow().isoformat() + 'Z'
        service = self._get_service()
        result = service.events().list(calendarId='primary', timeMin=now,
                                       maxResults=max_results, singleEvents=True,
                                       orderBy='startTime').execute()

        events = result.get('items', [])
        return events


    def _get_service(self, scope=None):
        if scope is None:
            scope = self.scopes[0]

        credentials = self.credentials[scope]
        http = credentials.authorize(httplib2.Http())
        return discovery.build('calendar', 'v3', http=http, cache_discovery=False)


# vim:sw=4:ts=4:et:

