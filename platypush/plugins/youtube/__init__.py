from typing import Any, Collection, Dict, List, Optional, Type

from platypush.plugins import Plugin, action

from .backends import BaseBackend, PipedBackend, InvidiousBackend


class YoutubePlugin(Plugin):
    r"""
    YouTube plugin.

    Unlike other Google plugins, this plugin doesn't rely on the Google API.

    That's because the official YouTube API has been subject to many changes to
    prevent scraping, and it requires the user to tinker with the OAuth layer,
    app permissions and app validation in order to get it working.

    Instead, it relies on an `Invidious <https://github.com/iv-org/invidious>`_
    or `Piped <https://docs.piped.video/>`_ instance, two open-source
    alternative YouTube frontends.

    You can specify a Piped/Inviodious instance configuration in the plugin
    configuration through the ``backends`` parameter:

        .. code-block:: yaml

            youtube:
                backends:
                    # For Piped
                    piped:
                        instance_url: https://pipedapi.kavin.rocks
                        auth_token: <auth_token>
                        frontend_url: https://piped.kavin.rocks

                    # For Invidious
                    invidious:
                        instance_url: https://yewtu.be
                        auth_token: <auth_token>

    Piped
    -----

    Parameters:

        - ``instance_url``: Base URL of the Piped instance (default:
          ``https://pipedapi.kavin.rocks``). **NOTE**: This should be the URL
          of the Piped API, not the Piped instance/frontend itself.
        - ``auth_token``: Optional authentication token from the Piped
          instance. This is required if you want to access your private feed
          and playlists, but not for searching public videos.
        - ``frontend_url``: Optional URL of the Piped frontend. This is needed
          to generate channels and playlists URLs. If not provided, the plugin
          will try and infer it by stripping the ``api`` string from
          ``instance_url``.

    In order to retrieve an authentication token:

      1. Login to your configured Piped instance.
      2. Copy the RSS/Atom feed URL on the _Feed_ tab.
      3. Copy the ``auth_token`` query parameter from the URL.
      4. Enter it in the ``auth_token`` field in the ``youtube`` section of the
         configuration file.

    Invidious
    ---------

    Parameters:

        - ``instance_url``: Base URL of the Invidious instance (default:
          ``https://yewtu.be``).
        - ``auth_token``: Optional authentication token from the Invidious
          instance. This is required if you want to access your private feed
          and playlists, but not for searching public videos.

    In order to retrieve an authentication token:

      1. Login to your configured Invidious instance.
      2. Open the URL ``https://<instance_url>/authorize_token?scopes=:*`` in
         your browser. Replace ``<instance_url>`` with the URL of your Invidious
         instance, and ``:*`` with the scopes you want to assign to the token
         (although an all-access token is recommended for full functionality).
      3. Copy the generated token.

    If both are provided, the Invidious backend will be used.

    If none is provided, the plugin will fallback to the default Invidious
    instance (``https://yewtu.be``), but authenticated actions will not be
    available.
    """

    _timeout = 20

    def __init__(
        self,
        backends: Optional[Dict[str, dict]] = None,
        **kwargs,
    ):
        """
        :param backends: Configuration for the backends.
        """
        super().__init__(**kwargs)
        piped = (backends or {}).get('piped')
        invidious = (backends or {}).get('invidious')

        if kwargs.get('piped_api_url'):
            piped = piped or {}
            self.logger.warning(
                'The "piped_api_url" parameter is deprecated. Use "piped.instance_url" instead.'
            )

            if not piped.get('instance_url'):
                piped['instance_url'] = kwargs['piped_api_url']

        if kwargs.get('auth_token'):
            piped = piped or {}
            self.logger.warning(
                'The "auth_token" parameter is deprecated. Use "piped.auth_token" instead.'
            )

            if not piped.get('auth_token'):
                piped['auth_token'] = kwargs['auth_token']

        self._backends: Dict[Type[BaseBackend], BaseBackend] = {}

        if piped is not None and invidious is not None:
            self.logger.warning(
                'Both "piped" and "invidious" parameters provided. '
                'Defaulting to "invidious".'
            )

        if piped is not None:
            self._backends[PipedBackend] = PipedBackend(**piped)
        if invidious is not None:
            self._backends[InvidiousBackend] = InvidiousBackend(**invidious)

        if piped is None and invidious is None:
            # Fallback to the default Invidious instance
            self._backends[InvidiousBackend] = InvidiousBackend()

    def _default_backend(self) -> BaseBackend:
        # Prefer Invidious over Piped
        if self._backends.get(InvidiousBackend):
            return self._backends[InvidiousBackend]

        return next(iter(self._backends.values()))

    def _get_backend(self, backend: Optional[str]) -> BaseBackend:
        if not backend:
            return self._default_backend()

        backend = backend.lower()
        for backend_instance in self._backends.values():
            if backend_instance.name == backend:
                return backend_instance

        raise ValueError(f'Unknown backend: {backend}')

    @action
    def search(self, query: str, backend: Optional[str] = None, **_) -> List[dict]:
        """
        Search for YouTube videos.

        :param query: Query string.
        :param backend: Optional backend to use. If not specified, the default
            one will be used.
        :return: .. schema:: piped.PipedVideoSchema(many=True)
        """
        api = self._get_backend(backend)
        self.logger.info(
            'Searching YouTube through the %s backend for "%s"', api.name, query
        )
        results = [item.to_dict() for item in api.search(query)]

        self.logger.info(
            '%d YouTube results for the search query "%s"',
            len(results),
            query,
        )

        return results

    @action
    def get_feed(
        self, page: Optional[Any] = None, backend: Optional[str] = None
    ) -> List[dict]:
        """
        Retrieve the YouTube feed.

        Depending on your account settings on the configured Piped instance,
        this may return either the latest videos uploaded by your subscribed
        channels (if you provided an authentication token), or the trending
        videos in the configured area (if you didn't).

        :param page: (Optional) ID/index of the page to retrieve.
        :param backend: Optional backend to use. If not specified, the default
            one will be used. This isn't supported by the Piped backend (all
            the videos are returned at once), and it's instead an integer >= 1
            on the Invidious backend.
        :return: .. schema:: piped.PipedVideoSchema(many=True)
        """
        return [
            item.to_dict() for item in self._get_backend(backend).get_feed(page=page)
        ]

    @action
    def get_playlists(self, backend: Optional[str] = None) -> List[dict]:
        """
        Retrieve the playlists saved by the user logged in to the Piped
        instance.

        :param backend: Optional backend to use. If not specified, the default
            one will be used.
        :return: .. schema:: piped.PipedPlaylistSchema(many=True)
        """
        return [item.to_dict() for item in self._get_backend(backend).get_playlists()]

    @action
    def get_playlist(
        self, id: str, backend: Optional[str] = None
    ) -> List[dict]:  # pylint: disable=redefined-builtin
        """
        Retrieve the videos in a playlist.

        :param id: Playlist ID as returned by the backend.
        :param backend: Optional backend to use. If not specified, the default
            one will be used.
        :return: .. schema:: piped.PipedVideoSchema(many=True)
        """
        return [item.to_dict() for item in self._get_backend(backend).get_playlist(id)]

    @action
    def get_subscriptions(self, backend: Optional[str] = None) -> List[dict]:
        """
        Retrieve the channels subscribed by the user logged in to the Piped
        instance.

        :param backend: Optional backend to use. If not specified, the default
            one will be used.
        :return: .. schema:: piped.PipedChannelSchema(many=True)
        """
        return [
            item.to_dict() for item in self._get_backend(backend).get_subscriptions()
        ]

    @action
    def get_channel(
        self,
        id: str,  # pylint: disable=redefined-builtin
        page: Optional[str] = None,
        backend: Optional[str] = None,
    ) -> dict:
        """
        Retrieve the information and videos of a channel given its ID or URL.

        :param id: Channel ID or URL.
        :param page: (Optional) ID/index of the page to retrieve.
        :param backend: Optional backend to use. If not specified, the default
            one will be used.
        :return: .. schema:: piped.PipedChannelSchema
        """
        return self._get_backend(backend).get_channel(id, page=page).to_dict()

    @action
    def add_to_playlist(
        self,
        playlist_id: str,
        item_ids: Optional[Collection[str]] = None,
        backend: Optional[str] = None,
        **kwargs,
    ):
        """
        Add a video to a playlist.

        :param playlist_id: Piped playlist ID.
        :param item_ids: YouTube IDs or URLs to add to the playlist.
        :param backend: Optional backend to use. If not specified, the default
            one will be used.
        """
        self._get_backend(backend).add_to_playlist(playlist_id, item_ids, **kwargs)

    @action
    def remove_from_playlist(
        self,
        playlist_id: str,
        item_ids: Optional[Collection[str]] = None,
        indices: Optional[Collection[int]] = None,
        backend: Optional[str] = None,
        **kwargs,
    ):
        """
        Remove a video from a playlist.

        Note that either ``item_ids`` or ``indices`` must be provided.

        :param item_ids: YouTube video IDs or URLs to remove from the playlist.
        :param indices: (0-based) indices of the items in the playlist to remove.
        :param playlist_id: Piped playlist ID.
        :param backend: Optional backend to use. If not specified, the default
            one will be used.
        """
        self._get_backend(backend).remove_from_playlist(
            playlist_id=playlist_id, item_ids=item_ids, indices=indices, **kwargs
        )

    @action
    def create_playlist(
        self,
        name: str,
        privacy: Optional[str] = 'private',
        backend: Optional[str] = None,
    ) -> dict:
        """
        Create a new playlist.

        :param name: Playlist name.
        :param backend: Optional backend to use. If not specified, the default
            one will be used.
        :param privacy: Privacy level of the playlist (only supported by
            Invidious). Supported values are:

                - ``private``: Only you can see the playlist.
                - ``public``: Everyone can see the playlist.
                - ``unlisted``: Everyone with the link can see the playlist.

        :return: Playlist information.
        """
        return (
            self._get_backend(backend).create_playlist(name, privacy=privacy).to_dict()
        )

    @action
    def edit_playlist(
        self,
        id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        privacy: Optional[str] = None,
        backend: Optional[str] = None,
    ):  # pylint: disable=redefined-builtin
        """
        Edit a playlist.

        :param id: Piped playlist ID.
        :param name: New playlist name.
        :param description: New playlist description.
        :param privacy: New privacy level of the playlist (only supported by
            Invidious). Supported values are:

                - ``private``: Only you can see the playlist.
                - ``public``: Everyone can see the playlist.
                - ``unlisted``: Everyone with the link can see the playlist.

        :param backend: Optional backend to use. If not specified, the default
            one will be used.
        """
        self._get_backend(backend).edit_playlist(
            id, name=name, description=description, privacy=privacy
        )

    @action
    def delete_playlist(
        self, id: str, backend: Optional[str] = None
    ):  # pylint: disable=redefined-builtin
        """
        Delete a playlist.

        :param id: Piped playlist ID.
        :param backend: Optional backend to use. If not specified, the default
            one will be used.
        """
        self._get_backend(backend).delete_playlist(id)

    @action
    def is_subscribed(self, channel_id: str, backend: Optional[str] = None) -> bool:
        """
        Check if the user is subscribed to a channel.

        :param channel_id: YouTube channel ID.
        :param backend: Optional backend to use. If not specified, the default
            one will be used.
        :return: True if the user is subscribed to the channel, False otherwise.
        """
        return self._get_backend(backend).is_subscribed(channel_id)

    @action
    def subscribe(self, channel_id: str, backend: Optional[str] = None):
        """
        Subscribe to a channel.

        :param channel_id: YouTube channel ID.
        :param backend: Optional backend to use. If not specified, the default
            one will be used.
        """
        self._get_backend(backend).subscribe(channel_id)

    @action
    def unsubscribe(self, channel_id: str, backend: Optional[str] = None):
        """
        Unsubscribe from a channel.

        :param channel_id: YouTube channel ID.
        :param backend: Optional backend to use. If not specified, the default
            one will be used.
        """
        self._get_backend(backend).unsubscribe(channel_id)


# vim:sw=4:ts=4:et:
