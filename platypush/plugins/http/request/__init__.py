import os
import requests

from platypush.message import Message
from platypush.plugins import Plugin, action


class HttpRequestPlugin(Plugin):
    """
    Plugin for executing custom HTTP requests.

    Requires:

        * **requests** (``pip install requests``)

    Some example usages::

        # Execute a GET request on a JSON endpoint
        {
            "type": "request",
            "action": "http.request.get",
            "args": {
                "url": "http://remote-host/api/v1/entity",
                "params": {
                    "start": "2000-01-01"
                }
            }
        }

        # Execute an action on another Platypush host through HTTP interface
        {
            "type": "request",
            "action": "http.request.post",
            "args": {
                "url": "http://remote-host:8008/execute",
                "json": {
                    "type": "request",
                    "target": "remote-host",
                    "action": "music.mpd.play"
                }
            }
        }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @staticmethod
    def _exec(method, url, output='text', **kwargs):
        """ Available output types: text (default), json, binary """

        if 'username' in kwargs and 'password' in kwargs:
            kwargs['auth'] = (kwargs.pop('username'), kwargs.pop('password'))

        method = getattr(requests, method)
        response = method(url, **kwargs)
        response.raise_for_status()

        if output == 'json':
            output = response.json()
        if output == 'binary':
            output = response.content
        else:
            output = response.text

        # noinspection PyBroadException
        try:
            # If the response is a Platypush JSON, extract it
            output = Message.build(output)
        except:
            pass

        return output

    @action
    def get(self, url, **kwargs):
        """
        Perform a GET request

        :param url: Target URL
        :type url: str

        :param kwargs: Additional arguments that will be transparently provided to the ``requests`` object, including
            but not limited to query params, data, JSON, headers etc.
            (see http://docs.python-requests.org/en/master/user/quickstart/#make-a-request)
        :type kwargs: dict
        """

        return self._exec(method='get', url=url, **kwargs)

    @action
    def post(self, url, **kwargs):
        """
        Perform a POST request

        :param url: Target URL
        :type url: str

        :param kwargs: Additional arguments that will be transparently provided to the ``requests`` object, including
            but not limited to query params, data, JSON, headers etc.
            (see http://docs.python-requests.org/en/master/user/quickstart/#make-a-request)
        :type kwargs: dict
        """

        return self._exec(method='post', url=url, **kwargs)

    @action
    def head(self, url, **kwargs):
        """
        Perform an HTTP HEAD request

        :param url: Target URL
        :type url: str

        :param kwargs: Additional arguments that will be transparently provided to the ``requests`` object, including
            but not limited to query params, data, JSON, headers etc.
            (see http://docs.python-requests.org/en/master/user/quickstart/#make-a-request)
        :type kwargs: dict
        """

        return self._exec(method='head', url=url, **kwargs)

    @action
    def put(self, url, **kwargs):
        """
        Perform a PUT request

        :param url: Target URL
        :type url: str

        :param kwargs: Additional arguments that will be transparently provided to the ``requests`` object, including
            but not limited to query params, data, JSON, headers etc.
            (see http://docs.python-requests.org/en/master/user/quickstart/#make-a-request)
        :type kwargs: dict
        """

        return self._exec(method='put', url=url, **kwargs)

    @action
    def delete(self, url, **kwargs):
        """
        Perform a DELETE request

        :param url: Target URL
        :type url: str

        :param kwargs: Additional arguments that will be transparently provided to the ``requests`` object, including
            but not limited to query params, data, JSON, headers etc.
            (see http://docs.python-requests.org/en/master/user/quickstart/#make-a-request)
        :type kwargs: dict
        """

        return self._exec(method='delete', url=url, **kwargs)

    @action
    def options(self, url, **kwargs):
        """
        Perform an HTTP OPTIONS request

        :param url: Target URL
        :type url: str

        :param kwargs: Additional arguments that will be transparently provided to the ``requests`` object, including
            but not limited to query params, data, JSON, headers etc.
            (see http://docs.python-requests.org/en/master/user/quickstart/#make-a-request)
        :type kwargs: dict
        """

        return self._exec(method='options', url=url, **kwargs)

    @action
    def download(self, url: str, path: str, **kwargs):
        """
        Locally download the content of a remote URL.

        :param url: URL to be downloaded.
        :param path: Path where the content will be downloaded on the local filesystem - must be a file name.
        """
        path = os.path.abspath(os.path.expanduser(path))
        content = self._exec(method='get', url=url, output='binary', **kwargs)

        with open(path, 'wb') as f:
            f.write(content)


# vim:sw=4:ts=4:et:
