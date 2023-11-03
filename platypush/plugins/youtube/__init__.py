from typing import Collection, Optional, Union
from platypush.plugins import action
from platypush.plugins.google import GooglePlugin


class YoutubePlugin(GooglePlugin):
    r"""
    YouTube plugin.

    Requirements:

        1. Create your Google application, if you don't have one already, on
           the `developers console <https://console.developers.google.com>`_.

        2. You may have to explicitly enable your user to use the app if the app
           is created in test mode. Go to "OAuth consent screen" and add your user's
           email address to the list of authorized users.

        3. Select the scopes that you want to enable for your application, depending
           on the integrations that you want to use.
           See https://developers.google.com/identity/protocols/oauth2/scopes
           for a list of the available scopes.

        4. Click on "Credentials", then "Create credentials" -> "OAuth client ID".

        5 Select "Desktop app", enter whichever name you like, and click "Create".

        6. Click on the "Download JSON" icon next to your newly created client ID.

        7. Generate a credentials file for the required scope:

            .. code-block:: bash

              mkdir -p <WORKDIR>/credentials/google
              python -m platypush.plugins.google.credentials \
                  'youtube.readonly' \
                  <WORKDIR>/credentials/google/client_secret.json

    """

    scopes = ['https://www.googleapis.com/auth/youtube.readonly']

    # See https://developers.google.com/youtube/v3/getting-started#part
    _default_parts = ['snippet']

    # See https://developers.google.com/youtube/v3/getting-started#resources
    _default_types = ['video']

    def __init__(self, *args, **kwargs):
        super().__init__(scopes=self.scopes, *args, **kwargs)

    @action
    def search(
        self,
        parts: Optional[Union[str, Collection[str]]] = None,
        query: str = '',
        types: Optional[Union[str, Collection[str]]] = None,
        max_results: int = 25,
        **kwargs
    ):
        """
        Search for YouTube content.

        :param parts: List of parts to get (default: snippet).
            See the `Getting started - Part
            <https://developers.google.com/youtube/v3/getting-started#part>`_.
        :param query: Query string (default: empty string)
        :param types: List of types to retrieve (default: video).
            See the `Getting started - Resources
            <https://developers.google.com/youtube/v3/getting-started#resources>`_.
        :param max_results: Maximum number of items that will be returned (default: 25).
        :param kwargs: Any extra arguments that will be transparently passed to the YouTube API.
            See the `Getting started - parameters
            <https://developers.google.com/youtube/v3/docs/search/list#parameters>`_.
        :return: A list of YouTube resources.
            See the `Getting started - Resource
            <https://developers.google.com/youtube/v3/docs/search#resource>`_.
        """

        parts = parts or self._default_parts[:]
        if isinstance(parts, list):
            parts = ','.join(parts)

        types = types or self._default_types[:]
        if isinstance(types, list):
            types = ','.join(types)

        service = self.get_service('youtube', 'v3')
        result = (
            service.search()
            .list(part=parts, q=query, type=types, maxResults=max_results, **kwargs)
            .execute()
        )

        events = result.get('items', [])
        return events


# vim:sw=4:ts=4:et:
