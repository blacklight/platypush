import requests
from typing import Callable, Dict, Any, List

from platypush.plugins import Plugin, action


class TravisciPlugin(Plugin):
    """
    `Travis-Ci <https://travis-ci.org/>`_ continuous integration plugin.

    Setup:

        - Get your API token from your `Travis-Ci account settings page <https://travis-ci.org/account/preferences>`_.

    """

    api_base_url = 'https://api.travis-ci.org/'

    def __init__(self, token: str, **kwargs):
        super().__init__(**kwargs)
        self.headers = {
            'Travis-API-Version': '3',
            'Authorization':  'token ' + token,
        }

    def _make_request(self, method: Callable, endpoint: str, **kwargs):
        url = self.api_base_url + endpoint
        response = method(url, headers=self.headers, **kwargs).json()
        if response.get('@type') == 'error':
            raise AssertionError('{type}: {message}'.
                                 format(type=response.get('error_type'), message=response.get('error_message')))

        return response

    @action
    def repos(self) -> Dict[str, Dict[str, Any]]:
        """
        Get the repos owned by current user.
        :return: Repo name -> Repo attributes mapping.
        """
        return {
            repo['name']: repo
            for repo in self._make_request(requests.get, endpoint='repos').get('repositories', [])
        }

    @action
    def builds(self, limit: int = 100) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get the list of builds triggered on the owned repositories

        :param limit: Maximum number of builds to be retrieved (default: 100).
        :return: Repo name -> List of builds
        """
        return self._make_request(requests.get, endpoint='builds').get('builds', [])[:limit]


# vim:sw=4:ts=4:et:
