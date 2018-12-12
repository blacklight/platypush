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


class GoogleYoutubePlugin(GooglePlugin, CalendarInterface):
    """
    YouTube plugin
    """

    scopes = ['https://www.googleapis.com/auth/youtube.readonly']

    # See https://developers.google.com/youtube/v3/getting-started#part
    _default_parts = ['snippet']

    # See https://developers.google.com/youtube/v3/getting-started#resources
    _default_types = ['video']


    def __init__(self, *args, **kwargs):
        super().__init__(scopes=self.scopes, *args, **kwargs)


    @action
    def search(self, parts=None, query='', types=None, max_results=25, **kwargs):
        """
        Search for YouTube content.

        :param parts: List of parts to get (default: snippet). See the `YouTube API documentation <https://developers.google.com/youtube/v3/getting-started#part>`_.
        :type parts: list[str] or str

        :param query: Query string (default: empty string)
        :type query: str

        :param types: List of types to retrieve (default: video). See the `YouTube API documentation <https://developers.google.com/youtube/v3/getting-started#resources>`_.
        :type types: list[str] or str

        :param max_results: Maximum number of items that will be returned (default: 25).
        :type max_results: int

        :param kwargs: Any extra arguments that will be transparently passed to the YouTube API, see the `YouTube API documentation <https://developers.google.com/youtube/v3/docs/search/list#parameters>`_.

        :return: A list of YouTube resources, see the `YouTube API documentation <https://developers.google.com/youtube/v3/docs/search#resource>`_.
        """

        parts = parts or self._default_parts[:]
        if isinstance(parts, list):
            parts = ','.join(parts)

        types = types or self._default_types[:]
        if isinstance(types, list):
            types = ','.join(types)

        service = self._get_service()
        result = service.search().list(part=parts, q=query, type=types,
                                       maxResults=max_results,
                                       **kwargs).execute()

        events = result.get('items', [])
        return events


    def _get_service(self, scope=None):
        if scope is None:
            scope = self.scopes[0]

        credentials = self.credentials[scope]
        http = credentials.authorize(httplib2.Http())
        return discovery.build('youtube', 'v3', http=http, cache_discovery=False)


# vim:sw=4:ts=4:et:

