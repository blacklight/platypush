import requests

from platypush.message.response import Response

from platypush.plugins import Plugin

class HttpRequestPlugin(Plugin):
    """ Plugin for executing custom HTTP requests """

    def _exec(self, method, url, output='text', **kwargs):
        """ Available output types: text (default), json, binary """

        method = getattr(requests, method)
        response = method(url, **kwargs)
        response.raise_for_status()
        output = response.text

        if output == 'json': output = response.json()
        if output == 'binary': output = response.content
        return Response(output=output, errors=[])


    def get(self, url, **kwargs):
        return self._exec(method='get', url=url, **kwargs)


    def post(self, url, **kwargs):
        return self._exec(method='post', url=url, **kwargs)


    def head(self, url, **kwargs):
        return self._exec(method='head', url=url, **kwargs)


    def put(self, url, **kwargs):
        return self._exec(method='put', url=url, **kwargs)


    def delete(self, url, **kwargs):
        return self._exec(method='delete', url=url, **kwargs)


    def options(self, url, **kwargs):
        return self._exec(method='options', url=url, **kwargs)


# vim:sw=4:ts=4:et:

