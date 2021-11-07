import os
import requests
from typing import Optional, Union, Iterable, Mapping, Sequence

from platypush.plugins import Plugin, action
from platypush.schemas.mastodon import MastodonSchema, MastodonSearchSchema, MastodonAccountCreationSchema, \
    MastodonAccountSchema, MastodonStatusSchema, MastodonFeaturedHashtagSchema, MastodonAccountListSchema, \
    MastodonFilterSchema, MastodonMediaSchema, MastodonConversationSchema, MastodonListSchema, \
    MastodonNotificationSchema
from platypush.utils import get_mime_type


class MastodonPlugin(Plugin):
    """
    Plugin to interact with `Mastodon <https://mastodon.social/about>`_ instances.

    It requires an active API token associated to an app registered on the instance.
    In order to get one:

        - Open ``https://<mastodon-base-url>/settings/applications/``
        - Create a new application
        - Select the scopes relevant for your specific usage.
        - Take note of the token reported on the *Your access token* row.

    The notifications subscription service requires the ``ngrok`` plugin and the
    `http` backend to be enabled, since we need to expose an external URL that
    the Mastodon instance can call when new events occur.
    """

    class SubscriptionConfig:
        tunnel_url: str
        local_port: int
        auth_secret: str
        private_key: str
        public_key: str
        server_key: str

    def __init__(self, base_url: str, access_token: Optional[str] = None, **kwargs):
        """
        :param base_url: Base URL of the Mastodon web server, in the form of ``https://<domain-name>``.
        :param access_token: Access token as reported on ``https://<base_url>/settings/applications/<app_id>``.
        """
        super().__init__(**kwargs)
        self._base_url = base_url
        self._access_token = access_token
        self._subscription_config = self.SubscriptionConfig()

    def base_url(self, version: str, base_url: Optional[str] = None) -> str:
        return f'{base_url or self._base_url}/api/{version}'

    def _run(
            self, path: str, method: str = 'get', version: str = 'v2', headers: Optional[dict] = None,
            base_url: Optional[str] = None, access_token: Optional[str] = None,
            schema: Optional[MastodonSchema] = None, **kwargs
    ) -> Optional[Union[dict, list]]:
        headers = {
            'Authorization': f'Bearer {access_token or self._access_token}',
            'Accept': 'application/json',
            **(headers or {}),
        }

        method = getattr(requests, method.lower())
        rs = method(self.base_url(base_url=base_url, version=version) + '/' + path, headers=headers, **kwargs)
        rs.raise_for_status()
        rs = rs.json()
        if schema:
            rs = schema.dump(rs)
        return rs

    # noinspection PyShadowingBuiltins
    @action
    def search(
            self, query: str, type: Optional[str] = None, min_id: Optional[str] = None,
            max_id: Optional[str] = None, limit: int = 20, offset: int = 0, following: bool = False,
            **kwargs
    ) -> Mapping[str, Iterable[dict]]:
        """
        Perform a search.

        :param query: Search query.
        :param type: Filter by type. Supported types:

            - ``accounts``
            - ``hashtags``
            - ``statuses``

        :param min_id: Return results newer than this ID.
        :param max_id: Return results older than this ID.
        :param limit: Maximum number of results (default: 20).
        :param offset: Return results from this offset (default: 0).
        :param following: Only return results from accounts followed by the user (default: False).
        :param kwargs: ``base_url``/``access_token`` override.
        :return: .. schema:: mastodon.MastodonSearchSchema
        """
        return self._run(
            'search',
            version='v2',
            schema=MastodonSearchSchema(),
            params={
                'q': query,
                **({'type': type} if type else {}),
                **({'min_id': min_id} if min_id else {}),
                **({'max_id': max_id} if max_id else {}),
                **({'limit': limit} if limit else {}),
                **({'offset': offset} if offset else {}),
                **({'following': following} if following else {}),
            }, **kwargs
        )

    @action
    def register_account(
            self, username: str, email: str, password: str, locale: str = 'en',
            reason: Optional[str] = None, **kwargs
    ) -> dict:
        """
        Register a new account.

        It requires the specified API token to have ``write:accounts`` permissions.

        :param username: User name.
        :param email: User's email address (must be a valid address).
        :param password: The password used for the first login.
        :param locale: Language/encoding for the confirmation email.
        :param reason: Text that will be reviewed by moderators if registrations require manual approval.
        :param kwargs: ``base_url``/``access_token`` override.
        :return: .. schema:: mastodon.MastodonAccountCreationSchema
        """
        return self._run(
            'accounts',
            method='post',
            version='v1',
            schema=MastodonAccountCreationSchema(),
            json={
                'username': username,
                'email': email,
                'password': password,
                'locale': locale,
                'reason': reason,
                'agreement': True,
            }, **kwargs
        )

    @action
    def update_account(
            self, discoverable: Optional[bool] = None, bot: Optional[bool] = None,
            display_name: Optional[str] = None, note: Optional[str] = None,
            avatar: Optional[str] = None, header: Optional[str] = None,
            locked: Optional[bool] = None, privacy: Optional[str] = None,
            sensitive: Optional[bool] = None, language: Optional[str] = None,
            metadata: Optional[Iterable[Mapping]] = None, **kwargs
    ) -> dict:
        """
        Updates the properties of the account associated to the access token.

        It requires the specified API token to have ``write:accounts`` permissions.

        :param discoverable: Whether the account should be shown in the profile directory.
        :param bot: Whether the account is a bot.
        :param display_name: The display name to use for the profile.
        :param note: The account bio (HTML is supported).
        :param avatar: Path to an avatar image.
        :param header: Path to a header image.
        :param locked: Whether manual approval of follow requests is required.
        :param privacy: Default post privacy for authored statuses.
        :param sensitive: Whether to mark authored statuses as sensitive by default.
        :param language: Default language to use for authored statuses (ISO 6391 code).
        :param metadata: Profile metadata items with ``name`` and ``value``.
        :param kwargs: ``base_url``/``access_token`` override.
        :return: .. schema:: mastodon.MastodonAccountSchema
        """
        avatar = os.path.expanduser(avatar) if avatar else None
        header = os.path.expanduser(header) if header else None
        return self._run(
            'accounts/update_credentials',
            method='patch',
            version='v1',
            schema=MastodonAccountSchema(),
            data={
                **({'discoverable': discoverable} if discoverable is not None else {}),
                **({'bot': bot} if bot is not None else {}),
                **({'display_name': display_name} if display_name is not None else {}),
                **({'note': note} if note is not None else {}),
                **({'locked': locked} if locked is not None else {}),
                **({'source[privacy]': privacy} if privacy is not None else {}),
                **({'source[sensitive]': sensitive} if sensitive is not None else {}),
                **({'source[language]': language} if language is not None else {}),
                **({'fields_attributes': metadata} if metadata is not None else {}),
            },
            files={
                **({'avatar': (
                    os.path.basename(avatar), open(avatar, 'rb'), get_mime_type(avatar)
                )} if avatar is not None else {}),
                **({'header': (
                    os.path.basename(header), open(header, 'rb'), get_mime_type(header)
                )} if header is not None else {}),
            },
            **kwargs
        )

    @action
    def get_account(self, account_id: str, **kwargs) -> dict:
        """
        Retrieve an account by ID.

        It requires the specified API token to have ``read:accounts`` permissions.

        :param account_id: Account ID to retrieve.
        :param kwargs: ``base_url``/``access_token`` override.
        :return: .. schema:: mastodon.MastodonAccountSchema
        """
        return self._run(
            f'accounts/{account_id}',
            version='v1',
            schema=MastodonAccountSchema(),
            **kwargs
        )

    @action
    def get_statuses(self, account_id: str, min_id: Optional[str] = None, max_id: Optional[str] = None,
                     limit: int = 20, offset: int = 0, **kwargs) -> Iterable[dict]:
        """
        Retrieve statuses by account ID.

        It requires the specified API token to have the ``read:statuses`` permission.

        :param account_id: Account ID.
        :param min_id: Return results newer than this ID.
        :param max_id: Return results older than this ID.
        :param limit: Maximum number of results (default: 20).
        :param offset: Return results from this offset (default: 0).
        :param kwargs: ``base_url``/``access_token`` override.
        :return: .. schema:: mastodon.MastodonStatusSchema(many=True)
        """
        return self._run(
            f'accounts/{account_id}/statuses',
            version='v1',
            schema=MastodonStatusSchema(many=True),
            params={
                **({'min_id': min_id} if min_id else {}),
                **({'max_id': max_id} if max_id else {}),
                **({'limit': limit} if limit else {}),
                **({'offset': offset} if offset else {}),
            },
            **kwargs
        )

    @action
    def get_followers(self, account_id: str, max_id: Optional[str] = None,
                      since_id: Optional[str] = None, limit: int = 20, offset: int = 0,
                      **kwargs) -> Iterable[dict]:
        """
        Retrieve the list of followers of an account.

        It requires the specified API token to have the ``read:accounts`` permission.

        :param account_id: Account ID.
        :param max_id: Return results older than this ID.
        :param since_id: Return results newer than this ID.
        :param limit: Maximum number of results (default: 20).
        :param offset: Return results from this offset (default: 0).
        :param kwargs: ``base_url``/``access_token`` override.
        :return: .. schema:: mastodon.MastodonAccountSchema(many=True)
        """
        return self._run(
            f'accounts/{account_id}/followers',
            version='v1',
            schema=MastodonAccountSchema(many=True),
            params={
                **({'since_id': since_id} if since_id else {}),
                **({'max_id': max_id} if max_id else {}),
                **({'limit': limit} if limit else {}),
                **({'offset': offset} if offset else {}),
            },
            **kwargs
        )

    @action
    def get_following(self, account_id: str, max_id: Optional[str] = None,
                      since_id: Optional[str] = None, limit: int = 20, offset: int = 0,
                      **kwargs) -> Iterable[dict]:
        """
        Retrieve the list of accounts followed by a specified account.

        It requires the specified API token to have the ``read:accounts`` permission.

        :param account_id: Account ID.
        :param max_id: Return results older than this ID.
        :param since_id: Return results newer than this ID.
        :param limit: Maximum number of results (default: 20).
        :param offset: Return results from this offset (default: 0).
        :param kwargs: ``base_url``/``access_token`` override.
        :return: .. schema:: mastodon.MastodonAccountSchema(many=True)
        """
        return self._run(
            f'accounts/{account_id}/following',
            version='v1',
            schema=MastodonAccountSchema(many=True),
            params={
                **({'since_id': since_id} if since_id else {}),
                **({'max_id': max_id} if max_id else {}),
                **({'limit': limit} if limit else {}),
                **({'offset': offset} if offset else {}),
            },
            **kwargs
        )

    @action
    def get_featured_tags(self, account_id: Optional[str] = None, max_id: Optional[str] = None,
                          since_id: Optional[str] = None, limit: int = 20, offset: int = 0,
                          **kwargs) -> Iterable[dict]:
        """
        Retrieve the list of featured hashtags of an account.

        It requires the specified API token to have the ``read:accounts`` permission.

        :param account_id: Account ID (if not specified then retrieve the featured tags of the current account).
        :param max_id: Return results older than this ID.
        :param since_id: Return results newer than this ID.
        :param limit: Maximum number of results (default: 20).
        :param offset: Return results from this offset (default: 0).
        :param kwargs: ``base_url``/``access_token`` override.
        :return: .. schema:: mastodon.MastodonFeaturedHashtagSchema(many=True)
        """
        return self._run(
            f'accounts/{account_id}/featured_tags' if account_id else 'featured_tags',
            version='v1',
            schema=MastodonFeaturedHashtagSchema(many=True),
            params={
                **({'since_id': since_id} if since_id else {}),
                **({'max_id': max_id} if max_id else {}),
                **({'limit': limit} if limit else {}),
                **({'offset': offset} if offset else {}),
            },
            **kwargs
        )

    @action
    def get_featured_lists(self, account_id: str, max_id: Optional[str] = None,
                           since_id: Optional[str] = None, limit: int = 20, offset: int = 0,
                           **kwargs) -> Iterable[dict]:
        """
        Retrieve the list that you have added a certain account to.

        It requires the specified API token to have the ``read:lists`` permission.

        :param account_id: Account ID.
        :param max_id: Return results older than this ID.
        :param since_id: Return results newer than this ID.
        :param limit: Maximum number of results (default: 20).
        :param offset: Return results from this offset (default: 0).
        :param kwargs: ``base_url``/``access_token`` override.
        :return: .. schema:: mastodon.MastodonAccountListSchema(many=True)
        """
        return self._run(
            f'accounts/{account_id}/lists',
            version='v1',
            schema=MastodonAccountListSchema(many=True),
            params={
                **({'since_id': since_id} if since_id else {}),
                **({'max_id': max_id} if max_id else {}),
                **({'limit': limit} if limit else {}),
                **({'offset': offset} if offset else {}),
            },
            **kwargs
        )

    @action
    def follow_account(self, account_id: str, notify: bool = False, reblogs: bool = True, **kwargs):
        """
        Follow a given account ID.

        It requires the specified API token to have the ``write:follows`` permission.

        :param account_id: Account ID.
        :param notify: Receive notifications when this account posts a new status (default: False).
        :param reblogs: Receive this account's reblogs on your timeline (default: True).
        :param kwargs: ``base_url``/``access_token`` override.
        """
        self._run(
            f'accounts/{account_id}/follow',
            version='v1',
            method='post',
            json={'notify': notify, 'reblogs': reblogs},
            **kwargs
        )

    @action
    def unfollow_account(self, account_id: str, **kwargs):
        """
        Unfollow a given account ID.

        It requires the specified API token to have the ``write:follows`` permission.

        :param account_id: Account ID.
        :param kwargs: ``base_url``/``access_token`` override.
        """
        self._run(
            f'accounts/{account_id}/unfollow',
            version='v1',
            method='post',
            **kwargs
        )

    @action
    def block_account(self, account_id: str, **kwargs):
        """
        Block a given account ID.

        It requires the specified API token to have the ``write:blocks`` permission.

        :param account_id: Account ID.
        :param kwargs: ``base_url``/``access_token`` override.
        """
        self._run(
            f'accounts/{account_id}/block',
            version='v1',
            method='post',
            **kwargs
        )

    @action
    def unblock_account(self, account_id: str, **kwargs):
        """
        Unblock a given account ID.

        It requires the specified API token to have the ``write:blocks`` permission.

        :param account_id: Account ID.
        :param kwargs: ``base_url``/``access_token`` override.
        """
        self._run(
            f'accounts/{account_id}/unblock',
            version='v1',
            method='post',
            **kwargs
        )

    @action
    def mute_account(self, account_id: str, **kwargs):
        """
        Mute a given account ID.

        It requires the specified API token to have the ``write:mutes`` permission.

        :param account_id: Account ID.
        :param kwargs: ``base_url``/``access_token`` override.
        """
        self._run(
            f'accounts/{account_id}/mute',
            version='v1',
            method='post',
            **kwargs
        )

    @action
    def unmute_account(self, account_id: str, **kwargs):
        """
        Unmute a given account ID.

        It requires the specified API token to have the ``write:mutes`` permission.

        :param account_id: Account ID.
        :param kwargs: ``base_url``/``access_token`` override.
        """
        self._run(
            f'accounts/{account_id}/unmute',
            version='v1',
            method='post',
            **kwargs
        )

    @action
    def pin_account(self, account_id: str, **kwargs):
        """
        Pin a given account ID to your profile.

        It requires the specified API token to have the ``write:accounts`` permission.

        :param account_id: Account ID.
        :param kwargs: ``base_url``/``access_token`` override.
        """
        self._run(
            f'accounts/{account_id}/pin',
            version='v1',
            method='post',
            **kwargs
        )

    @action
    def unpin_account(self, account_id: str, **kwargs):
        """
        Unpin a given account ID from your profile.

        It requires the specified API token to have the ``write:accounts`` permission.

        :param account_id: Account ID.
        :param kwargs: ``base_url``/``access_token`` override.
        """
        self._run(
            f'accounts/{account_id}/unpin',
            version='v1',
            method='post',
            **kwargs
        )

    @action
    def set_account_note(self, account_id: str, note: str, **kwargs):
        """
        Set a private note for an account.

        It requires the specified API token to have the ``write:accounts`` permission.

        :param account_id: Account ID.
        :param note: Note content (HTML is supported).
        :param kwargs: ``base_url``/``access_token`` override.
        """
        self._run(
            f'accounts/{account_id}/note',
            version='v1',
            method='post',
            json={'comment': note},
            **kwargs
        )

    @action
    def get_bookmarked_statuses(self, min_id: Optional[str] = None,
                                max_id: Optional[str] = None, limit: int = 20, **kwargs) -> Iterable[dict]:
        """
        Retrieve the list of statuses bookmarked by the user.

        It requires the specified API token to have the ``read:bookmarks`` permission.

        :param min_id: Return results newer than this ID.
        :param max_id: Return results older than this ID.
        :param limit: Maximum number of results (default: 20).
        :param kwargs: ``base_url``/``access_token`` override.
        :return: .. schema:: mastodon.MastodonStatusSchema(many=True)
        """
        return self._run(
            'bookmarks',
            version='v1',
            schema=MastodonStatusSchema(many=True),
            params={
                **({'min_id': min_id} if min_id else {}),
                **({'max_id': max_id} if max_id else {}),
                **({'limit': limit} if limit else {}),
            },
            **kwargs
        )

    @action
    def get_favourited_statuses(self, min_id: Optional[str] = None,
                                max_id: Optional[str] = None, limit: int = 20, **kwargs) -> Iterable[dict]:
        """
        Retrieve the list of statuses favourited by the account.

        It requires the specified API token to have the ``read:favourites`` permission.

        :param min_id: Return results newer than this ID.
        :param max_id: Return results older than this ID.
        :param limit: Maximum number of results (default: 20).
        :param kwargs: ``base_url``/``access_token`` override.
        :return: .. schema:: mastodon.MastodonStatusSchema(many=True)
        """
        return self._run(
            'favourites',
            version='v1',
            schema=MastodonStatusSchema(many=True),
            params={
                **({'min_id': min_id} if min_id else {}),
                **({'max_id': max_id} if max_id else {}),
                **({'limit': limit} if limit else {}),
            },
            **kwargs
        )

    @action
    def get_muted_accounts(self, max_id: Optional[str] = None,
                           since_id: Optional[str] = None, limit: int = 20,
                           **kwargs) -> Iterable[dict]:
        """
        Retrieve the list of muted accounts.

        It requires the specified API token to have the ``read:mutes`` permission.

        :param max_id: Return results older than this ID.
        :param since_id: Return results newer than this ID.
        :param limit: Maximum number of results (default: 20).
        :param kwargs: ``base_url``/``access_token`` override.
        :return: .. schema:: mastodon.MastodonAccountSchema(many=True)
        """
        return self._run(
            'mutes',
            version='v1',
            schema=MastodonAccountSchema(many=True),
            params={
                **({'since_id': since_id} if since_id else {}),
                **({'max_id': max_id} if max_id else {}),
                **({'limit': limit} if limit else {}),
            },
            **kwargs
        )

    @action
    def get_blocked_accounts(self, max_id: Optional[str] = None,
                             since_id: Optional[str] = None, limit: int = 20,
                             **kwargs) -> Iterable[dict]:
        """
        Retrieve the list of blocked accounts.

        It requires the specified API token to have the ``read:blocks`` permission.

        :param max_id: Return results older than this ID.
        :param since_id: Return results newer than this ID.
        :param limit: Maximum number of results (default: 20).
        :param kwargs: ``base_url``/``access_token`` override.
        :return: .. schema:: mastodon.MastodonAccountSchema(many=True)
        """
        return self._run(
            'blocks',
            version='v1',
            schema=MastodonAccountSchema(many=True),
            params={
                **({'since_id': since_id} if since_id else {}),
                **({'max_id': max_id} if max_id else {}),
                **({'limit': limit} if limit else {}),
            },
            **kwargs
        )

    @action
    def get_filters(self, **kwargs) -> Iterable[dict]:
        """
        Retrieve the list of filters created by the account.

        It requires the specified API token to have the ``read:filters`` permission.

        :param kwargs: ``base_url``/``access_token`` override.
        :return: .. schema:: mastodon.MastodonFilterSchema(many=True)
        """
        return self._run(
            'filters',
            version='v1',
            schema=MastodonFilterSchema(many=True),
            **kwargs
        )

    @action
    def create_filter(self, phrase: str, context: Iterable[str],
                      irreversible: Optional[bool] = None,
                      whole_word: Optional[bool] = None,
                      expires_in: Optional[int] = None,
                      **kwargs) -> dict:
        """
        Create a new filter.

        It requires the specified API token to have the ``write:filters`` permission.

        :param phrase: Text to be filtered.
        :param context: Array of enumerable strings: ``home``, ``notifications``, ``public``, ``thread``.
            At least one context must be specified.
        :param irreversible: Should the server irreversibly drop matching entities from home and notifications?
        :param whole_word: Consider word boundaries?
        :param expires_in: Expires in the specified number of seconds.
        :param kwargs: ``base_url``/``access_token`` override.
        :return: .. schema:: mastodon.MastodonFilterSchema
        """
        return self._run(
            'filters',
            version='v1',
            method='post',
            schema=MastodonFilterSchema(),
            json={
                'phrase': phrase,
                'context': context,
                **({'irreversible': irreversible} if irreversible is not None else {}),
                **({'whole_word': whole_word} if whole_word is not None else {}),
                **({'expires_in': expires_in} if expires_in is not None else {}),
            },
            **kwargs
        )

    @action
    def update_filter(self, filter_id: int,
                      phrase: Optional[str] = None,
                      context: Optional[Iterable[str]] = None,
                      irreversible: Optional[bool] = None,
                      whole_word: Optional[bool] = None,
                      expires_in: Optional[int] = None,
                      **kwargs) -> dict:
        """
        Update a filter.

        It requires the specified API token to have the ``write:filters`` permission.

        :param filter_id: Filter ID.
        :param phrase: Text to be filtered.
        :param context: Array of enumerable strings: ``home``, ``notifications``, ``public``, ``thread``.
            At least one context must be specified.
        :param irreversible: Should the server irreversibly drop matching entities from home and notifications?
        :param whole_word: Consider word boundaries?
        :param expires_in: Expires in the specified number of seconds.
        :param kwargs: ``base_url``/``access_token`` override.
        :return: .. schema:: mastodon.MastodonFilterSchema
        """
        return self._run(
            f'filters/{filter_id}',
            version='v1',
            method='put',
            schema=MastodonFilterSchema(),
            json={
                **({'phrase': phrase} if phrase is not None else {}),
                **({'context': context} if context is not None else {}),
                **({'irreversible': irreversible} if irreversible is not None else {}),
                **({'whole_word': whole_word} if whole_word is not None else {}),
                **({'expires_in': expires_in} if expires_in is not None else {}),
            },
            **kwargs
        )

    @action
    def remove_filter(self, filter_id: int, **kwargs):
        """
        Remove a filter.

        It requires the specified API token to have the ``write:filters`` permission.

        :param filter_id: Filter ID.
        :param kwargs: ``base_url``/``access_token`` override.
        """
        return self._run(
            f'filters/{filter_id}',
            version='v1',
            method='delete',
            **kwargs
        )

    @action
    def add_featured_tag(self, name: str, **kwargs) -> dict:
        """
        Add a featured tag to the current account.

        It requires the specified API token to have the ``write:accounts`` permission.

        :param name: Hashtag name.
        :param kwargs: ``base_url``/``access_token`` override.
        :return: .. schema:: mastodon.MastodonFeaturedHashtagSchema
        """
        return self._run(
            'featured_tags',
            version='v1',
            method='post',
            schema=MastodonFeaturedHashtagSchema(),
            json={'name': name},
            **kwargs
        )

    @action
    def remove_featured_tag(self, tag_id: int, **kwargs):
        """
        Remove a featured tag from the current account.

        It requires the specified API token to have the ``write:accounts`` permission.

        :param tag_id: Hashtag ID.
        :param kwargs: ``base_url``/``access_token`` override.
        """
        return self._run(
            f'featured_tags/{tag_id}',
            version='v1',
            method='delete',
            **kwargs
        )

    @action
    def publish_status(self, status: str, in_reply_to_id: Optional[str] = None,
                       media_ids: Optional[Iterable[str]] = None,
                       sensitive: Optional[bool] = None, spoiler_text: Optional[str] = None,
                       visibility: Optional[str] = None, **kwargs) -> dict:
        """
        Publish a new status.

        It requires the specified API token to have the ``write:statuses`` permission.

        :param status: Content of the status to publish.
        :param in_reply_to_id: Post the status in reply to this status ID.
        :param media_ids: Optional list of media IDs to add as attachments.
        :param sensitive: Set to true if sensitive.
        :param spoiler_text: Set for optional spoiler text.
        :param visibility: Supported values: ``public``, ``unlisted``, ``private`` and ``direct``.
        :param kwargs: ``base_url``/``access_token`` override.
        :return: .. schema:: mastodon.MastodonStatusSchema
        """
        return self._run(
            'statuses',
            version='v1',
            method='post',
            schema=MastodonStatusSchema(),
            json={
                'status': status,
                **({'in_reply_to_id': in_reply_to_id} if in_reply_to_id is None else {}),
                **({'media_ids': media_ids} if media_ids else {}),
                **({'sensitive': sensitive} if sensitive is None else {}),
                **({'spoiler_text': spoiler_text} if spoiler_text is None else {}),
                **({'visibility': visibility} if visibility is None else {}),
            },
            **kwargs
        )

    @action
    def get_status(self, status_id: str, **kwargs) -> dict:
        """
        Get a status by ID.

        It requires the specified API token to have the ``read:statuses`` permission.

        :param status_id: Status ID.
        :param kwargs: ``base_url``/``access_token`` override.
        :return: .. schema:: mastodon.MastodonStatusSchema
        """
        return self._run(
            f'statuses/{status_id}',
            version='v1',
            schema=MastodonStatusSchema(),
            **kwargs
        )

    @action
    def remove_status(self, status_id: str, **kwargs):
        """
        Remove a status by ID.

        It requires the specified API token to have the ``read:statuses`` permission.

        :param status_id: Status ID.
        :param kwargs: ``base_url``/``access_token`` override.
        """
        return self._run(
            f'statuses/{status_id}',
            version='v1',
            method='delete',
            **kwargs
        )

    @action
    def add_favourite_status(self, status_id: str, **kwargs):
        """
        Favourite a status.

        It requires the specified API token to have the ``write:favourites`` permission.

        :param status_id: Status ID.
        :param kwargs: ``base_url``/``access_token`` override.
        """
        return self._run(
            f'statuses/{status_id}/favourite',
            version='v1',
            method='post',
            **kwargs
        )

    @action
    def remove_favourite_status(self, status_id: str, **kwargs):
        """
        Undo a status favourite action.

        It requires the specified API token to have the ``write:favourites`` permission.

        :param status_id: Status ID.
        :param kwargs: ``base_url``/``access_token`` override.
        """
        return self._run(
            f'statuses/{status_id}/favourite',
            version='v1',
            method='delete',
            **kwargs
        )

    @action
    def reblog_status(self, status_id: str, **kwargs):
        """
        Reblog (a.k.a. reshare/boost) a status.

        It requires the specified API token to have the ``write:statuses`` permission.

        :param status_id: Status ID.
        :param kwargs: ``base_url``/``access_token`` override.
        """
        return self._run(
            f'statuses/{status_id}/reblog',
            version='v1',
            method='post',
            **kwargs
        )

    @action
    def undo_reblog_status(self, status_id: str, **kwargs):
        """
        Undo a status reblog.

        It requires the specified API token to have the ``write:statuses`` permission.

        :param status_id: Status ID.
        :param kwargs: ``base_url``/``access_token`` override.
        """
        return self._run(
            f'statuses/{status_id}/unreblog',
            version='v1',
            method='post',
            **kwargs
        )

    @action
    def bookmark_status(self, status_id: str, **kwargs):
        """
        Add a status to the bookmarks.

        It requires the specified API token to have the ``write:bookmarks`` permission.

        :param status_id: Status ID.
        :param kwargs: ``base_url``/``access_token`` override.
        """
        return self._run(
            f'statuses/{status_id}/bookmark',
            version='v1',
            method='post',
            **kwargs
        )

    @action
    def undo_bookmark_status(self, status_id: str, **kwargs):
        """
        Remove a status from the bookmarks.

        It requires the specified API token to have the ``write:bookmarks`` permission.

        :param status_id: Status ID.
        :param kwargs: ``base_url``/``access_token`` override.
        """
        return self._run(
            f'statuses/{status_id}/unbookmark',
            version='v1',
            method='post',
            **kwargs
        )

    @action
    def mute_status(self, status_id: str, **kwargs):
        """
        Mute updates on a status.

        It requires the specified API token to have the ``write:mutes`` permission.

        :param status_id: Status ID.
        :param kwargs: ``base_url``/``access_token`` override.
        """
        return self._run(
            f'statuses/{status_id}/mute',
            version='v1',
            method='post',
            **kwargs
        )

    @action
    def unmute_status(self, status_id: str, **kwargs):
        """
        Restore updates on a status.

        It requires the specified API token to have the ``write:mutes`` permission.

        :param status_id: Status ID.
        :param kwargs: ``base_url``/``access_token`` override.
        """
        return self._run(
            f'statuses/{status_id}/unmute',
            version='v1',
            method='post',
            **kwargs
        )

    @action
    def pin_status(self, status_id: str, **kwargs):
        """
        Pin a status to the profile.

        It requires the specified API token to have the ``write:accounts`` permission.

        :param status_id: Status ID.
        :param kwargs: ``base_url``/``access_token`` override.
        """
        return self._run(
            f'statuses/{status_id}/pin',
            version='v1',
            method='post',
            **kwargs
        )

    @action
    def unpin_status(self, status_id: str, **kwargs):
        """
        Remove a pinned status.

        It requires the specified API token to have the ``write:accounts`` permission.

        :param status_id: Status ID.
        :param kwargs: ``base_url``/``access_token`` override.
        """
        return self._run(
            f'statuses/{status_id}/unpin',
            version='v1',
            method='post',
            **kwargs
        )

    @action
    def upload_media(self, file: str, description: Optional[str] = None,
                     thumbnail: Optional[str] = None, **kwargs) -> dict:
        """
        Upload media that can be used as attachments.

        It requires the specified API token to have the ``write:media`` permission.

        :param file: Path to the file to upload.
        :param thumbnail: Path to the file thumbnail.
        :param description: Optional attachment description.
        :param kwargs: ``base_url``/``access_token`` override.
        :return: .. schema:: mastodon.MastodonMediaSchema
        """
        file_path = os.path.expanduser(file)
        thumbnail_path = os.path.expanduser(thumbnail) if thumbnail else None
        return self._run(
            'media',
            version='v1',
            method='post',
            schema=MastodonMediaSchema(),
            data={
                **({'description': description} if description else {}),
            },
            files={
                'file': (
                    os.path.basename(file_path), open(file_path, 'rb'), get_mime_type(file_path)
                ),
                **(
                    {
                        'thumbnail': (
                            os.path.basename(thumbnail_path),
                            open(os.path.expanduser(thumbnail_path), 'rb'),
                            get_mime_type(thumbnail_path)
                        ),
                    } if thumbnail_path else {}
                ),
            },
            **kwargs
        )

    @action
    def update_media(self, media_id: str, file: Optional[str] = None, description: Optional[str] = None,
                     thumbnail: Optional[str] = None, **kwargs) -> dict:
        """
        Update a media attachment.

        It requires the specified API token to have the ``write:media`` permission.

        :param media_id: Media ID to update.
        :param file: Path to the new file.
        :param description: New description.
        :param thumbnail: Path to the new thumbnail.
        :param kwargs: ``base_url``/``access_token`` override.
        :return: .. schema:: mastodon.MastodonMediaSchema
        """
        file = os.path.expanduser(file)
        thumbnail = os.path.expanduser(thumbnail)
        return self._run(
            f'media/{media_id}',
            version='v1',
            method='put',
            schema=MastodonMediaSchema(),
            data={
                **({'description': description} if description else {}),
            },
            files={
                'file': (
                    os.path.basename(file), open(file, 'rb'), get_mime_type(file)
                ),
                **(
                    {
                        'thumbnail': (
                            os.path.basename(thumbnail),
                            open(os.path.expanduser(thumbnail), 'rb'),
                            get_mime_type(thumbnail)
                        ),
                    } if thumbnail else {}
                ),
            },
            **kwargs
        )

    @action
    def get_public_timeline(
            self, local: bool = False, remote: bool = False, only_media: bool = False,
            min_id: Optional[str] = None, max_id: Optional[str] = None, limit: int = 20,
            offset: int = 0, **kwargs
    ) -> Iterable[dict]:
        """
        Get a list of statuses from the public timeline.

        It requires the specified API token to have the ``read:statuses`` permission.

        :param local: Retrieve only local statuses (default: ``False``).
        :param remote: Retrieve only remote statuses (default: ``False``).
        :param only_media:  Retrieve only statuses with media attached (default: ``False``).
        :param min_id: Return results newer than this ID.
        :param max_id: Return results older than this ID.
        :param limit: Maximum number of results (default: 20).
        :param offset: Return results from this offset (default: 0).
        :param kwargs: ``base_url``/``access_token`` override.
        :return: .. schema:: mastodon.MastodonStatusSchema(many=True)
        """
        return self._run(
            'timelines/public',
            version='v1',
            schema=MastodonStatusSchema(many=True),
            params={
                **({'local': local} if local else {}),
                **({'remote': remote} if remote else {}),
                **({'only_media': only_media} if only_media else {}),
                **({'min_id': min_id} if min_id else {}),
                **({'max_id': max_id} if max_id else {}),
                **({'limit': limit} if limit else {}),
                **({'offset': offset} if offset else {}),
            }, **kwargs
        )

    @action
    def get_hashtag_timeline(
            self, hashtag: str, local: bool = False, only_media: bool = False,
            min_id: Optional[str] = None, max_id: Optional[str] = None, limit: int = 20,
            offset: int = 0, **kwargs
    ) -> Iterable[dict]:
        """
        Get a list of statuses associated to a hashtag.

        It requires the specified API token to have the ``read:statuses`` permission.

        :param hashtag: Hashtag to search.
        :param local: Retrieve only local statuses (default: ``False``).
        :param only_media:  Retrieve only statuses with media attached (default: ``False``).
        :param min_id: Return results newer than this ID.
        :param max_id: Return results older than this ID.
        :param limit: Maximum number of results (default: 20).
        :param offset: Return results from this offset (default: 0).
        :param kwargs: ``base_url``/``access_token`` override.
        :return: .. schema:: mastodon.MastodonStatusSchema(many=True)
        """
        return self._run(
            f'timelines/tag/{hashtag}',
            version='v1',
            schema=MastodonStatusSchema(many=True),
            params={
                **({'local': local} if local else {}),
                **({'only_media': only_media} if only_media else {}),
                **({'min_id': min_id} if min_id else {}),
                **({'max_id': max_id} if max_id else {}),
                **({'limit': limit} if limit else {}),
                **({'offset': offset} if offset else {}),
            }, **kwargs
        )

    @action
    def get_home_timeline(
            self, local: bool = False, only_media: bool = False,
            min_id: Optional[str] = None, max_id: Optional[str] = None, limit: int = 20,
            offset: int = 0, **kwargs
    ) -> Iterable[dict]:
        """
        Get a list of statuses from the followed users.

        It requires the specified API token to have the ``read:statuses`` permission.

        :param local: Retrieve only local statuses (default: ``False``).
        :param only_media:  Retrieve only statuses with media attached (default: ``False``).
        :param min_id: Return results newer than this ID.
        :param max_id: Return results older than this ID.
        :param limit: Maximum number of results (default: 20).
        :param offset: Return results from this offset (default: 0).
        :param kwargs: ``base_url``/``access_token`` override.
        :return: .. schema:: mastodon.MastodonStatusSchema(many=True)
        """
        return self._run(
            f'timelines/home',
            version='v1',
            schema=MastodonStatusSchema(many=True),
            params={
                **({'local': local} if local else {}),
                **({'only_media': only_media} if only_media else {}),
                **({'min_id': min_id} if min_id else {}),
                **({'max_id': max_id} if max_id else {}),
                **({'limit': limit} if limit else {}),
                **({'offset': offset} if offset else {}),
            }, **kwargs
        )

    @action
    def get_list_timeline(
            self, list_id: str,
            min_id: Optional[str] = None, max_id: Optional[str] = None, limit: int = 20,
            offset: int = 0, **kwargs
    ) -> Iterable[dict]:
        """
        Get a list of statuses from a list timeline.

        It requires the specified API token to have the ``read:lists`` permission.

        :param list_id: List ID.
        :param min_id: Return results newer than this ID.
        :param max_id: Return results older than this ID.
        :param limit: Maximum number of results (default: 20).
        :param offset: Return results from this offset (default: 0).
        :param kwargs: ``base_url``/``access_token`` override.
        :return: .. schema:: mastodon.MastodonStatusSchema(many=True)
        """
        return self._run(
            f'timelines/list/{list_id}',
            version='v1',
            schema=MastodonStatusSchema(many=True),
            params={
                **({'min_id': min_id} if min_id else {}),
                **({'max_id': max_id} if max_id else {}),
                **({'limit': limit} if limit else {}),
                **({'offset': offset} if offset else {}),
            }, **kwargs
        )

    @action
    def get_conversations(
            self, min_id: Optional[str] = None, max_id: Optional[str] = None,
            limit: int = 20,  **kwargs
    ) -> Iterable[dict]:
        """
        Get a list of user conversations.

        It requires the specified API token to have the ``read:statuses`` permission.

        :param min_id: Return results newer than this ID.
        :param max_id: Return results older than this ID.
        :param limit: Maximum number of results (default: 20).
        :param kwargs: ``base_url``/``access_token`` override.
        :return: .. schema:: mastodon.MastodonConversationSchema(many=True)
        """
        return self._run(
            'conversations',
            version='v1',
            schema=MastodonConversationSchema(many=True),
            params={
                **({'min_id': min_id} if min_id else {}),
                **({'max_id': max_id} if max_id else {}),
                **({'limit': limit} if limit else {}),
            }, **kwargs
        )

    @action
    def remove_conversation(self, conversation_id: int, **kwargs):
        """
        Remove a conversation by ID.

        It requires the specified API token to have the ``write_conversations`` permission.

        :param conversation_id: Conversation ID.
        :param kwargs: ``base_url``/``access_token`` override.
        """
        return self._run(
            f'conversations/{conversation_id}',
            version='v1',
            method='delete',
            **kwargs
        )

    @action
    def mark_conversation_as_read(self, conversation_id: int, **kwargs):
        """
        Mark a conversation as read.

        It requires the specified API token to have the ``write_conversations`` permission.

        :param conversation_id: Conversation ID.
        :param kwargs: ``base_url``/``access_token`` override.
        """
        return self._run(
            f'conversations/{conversation_id}/read',
            version='v1',
            method='post',
            **kwargs
        )

    @action
    def get_lists(self, list_id: Optional[int] = None, **kwargs) -> Union[dict, Iterable[dict]]:
        """
        Get the lists owned by the logged user.

        It requires the specified API token to have the ``read:lists`` permission.

        :param list_id: Retrieve a specific list ID (default: retrieve all).
        :param kwargs: ``base_url``/``access_token`` override.
        :return: .. schema:: mastodon.MastodonListSchema(many=True)
        """
        return self._run(
            'lists' + (f'/{list_id}' if list_id else ''),
            version='v1',
            method='get',
            schema=MastodonListSchema(many=list_id is None),
            **kwargs
        )

    @action
    def create_list(self, title: str, replies_policy: str = 'list', **kwargs) -> dict:
        """
        Create a new list.

        It requires the specified API token to have the ``write:lists`` permission.

        :param title: List title.
        :param replies_policy: Possible values: ``none``, ``following`` or ``list``. Default: ``list``.
        :param kwargs: ``base_url``/``access_token`` override.
        :return: .. schema:: mastodon.MastodonListSchema
        """
        return self._run(
            'lists',
            version='v1',
            method='post',
            schema=MastodonListSchema(),
            data={'title': title, 'replies_policy': replies_policy},
            **kwargs
        )

    @action
    def update_list(
            self, list_id: int, title: Optional[str], replies_policy: Optional[str] = None, **kwargs
    ) -> dict:
        """
        Update a list.

        It requires the specified API token to have the ``write:lists`` permission.

        :param list_id: List ID.
        :param title: New list title.
        :param replies_policy: New replies policy.
            Possible values: ``none``, ``following`` or ``list``. Default: ``list``.
        :param kwargs: ``base_url``/``access_token`` override.
        :return: .. schema:: mastodon.MastodonListSchema
        """
        return self._run(
            f'lists/{list_id}',
            version='v1',
            method='put',
            schema=MastodonListSchema(),
            data={
                **({'title': title} if title else {}),
                **({'replies_policy': replies_policy} if replies_policy else {}),
            },
            **kwargs
        )

    @action
    def delete_list(self, list_id: int, **kwargs):
        """
        Delete a list.

        It requires the specified API token to have the ``write:lists`` permission.

        :param list_id: List ID.
        :param kwargs: ``base_url``/``access_token`` override.
        """
        return self._run(
            f'lists/{list_id}',
            version='v1',
            method='delete',
            **kwargs
        )

    @action
    def get_list_accounts(
            self, list_id: Optional[int] = None, min_id: Optional[str] = None,
            max_id: Optional[str] = None, limit: int = 20, **kwargs
    ) -> Iterable[dict]:
        """
        Get the accounts in a list.

        It requires the specified API token to have the ``read:lists`` permission.

        :param list_id: List ID.
        :param min_id: Return results newer than this ID.
        :param max_id: Return results older than this ID.
        :param limit: Maximum number of results (default: 20).
        :param kwargs: ``base_url``/``access_token`` override.
        :return: .. schema:: mastodon.MastodonAccountSchema(many=True)
        """
        return self._run(
            f'lists/{list_id}/accounts',
            version='v1',
            method='get',
            schema=MastodonAccountSchema(many=True),
            params={
                **({'min_id': min_id} if min_id else {}),
                **({'max_id': max_id} if max_id else {}),
                **({'limit': limit} if limit else {}),
            },
            **kwargs
        )

    @action
    def add_accounts_to_list(self, list_id: int, account_ids: Sequence[str], **kwargs):
        """
        Add accounts to a list.

        It requires the specified API token to have the ``write:lists`` permission.

        :param list_id: List ID.
        :param account_ids: Accounts that should be added.
        :param kwargs: ``base_url``/``access_token`` override.
        :return: .. schema:: mastodon.MastodonListSchema
        """
        return self._run(
            f'lists/{list_id}/accounts',
            version='v1',
            method='post',
            data={'account_ids': account_ids},
            **kwargs
        )

    @action
    def remove_accounts_from_list(self, list_id: int, account_ids: Sequence[str], **kwargs):
        """
        Remove accounts from a list

        It requires the specified API token to have the ``write:lists`` permission.

        :param list_id: List ID.
        :param account_ids: Accounts that should be removed.
        :param kwargs: ``base_url``/``access_token`` override.
        :return: .. schema:: mastodon.MastodonListSchema
        """
        return self._run(
            f'lists/{list_id}/accounts',
            version='v1',
            method='delete',
            data={'account_ids': account_ids},
            **kwargs
        )

    @action
    def get_notifications(
            self, notification_id: Optional[str] = None, min_id: Optional[str] = None,
            max_id: Optional[str] = None, limit: int = 20, **kwargs
    ) -> Union[dict, Iterable[dict]]:
        """
        Get the list of notifications of the user.

        It requires the specified API token to have the ``read:notifications`` permission.

        :param notification_id: If specified then retrieve only the notification associated to this ID.
        :param min_id: Return results newer than this ID.
        :param max_id: Return results older than this ID.
        :param limit: Maximum number of results (default: 20).
        :param kwargs: ``base_url``/``access_token`` override.
        :return: .. schema:: mastodon.MastodonNotificationSchema(many=True)
        """
        rs = self._run(
            'notifications' + (f'/{notification_id}' if notification_id else ''),
            version='v1',
            method='get',
            schema=MastodonNotificationSchema(many=notification_id is None),
            params={
                **({'min_id': min_id} if min_id else {}),
                **({'max_id': max_id} if max_id else {}),
                **({'limit': limit} if limit else {}),
            },
            **kwargs
        )

        return rs

    @action
    def dismiss_notifications(self, notification_id: Optional[str] = None, **kwargs):
        """
        Dismiss notifications.

        It requires the specified API token to have the ``write:notifications`` permission.

        :param notification_id: Dismiss only this notification.
        :param kwargs: ``base_url``/``access_token`` override.
        """
        return self._run(
            'notifications/' + (
                f'{notification_id}/dismiss' if notification_id else 'clear'
            ),
            version='v1',
            method='post',
            **kwargs
        )


# vim:sw=4:ts=4:et:
