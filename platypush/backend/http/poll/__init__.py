import importlib
import time

from platypush.backend import Backend
from platypush.backend.http.request import HttpRequest


class HttpPollBackend(Backend):
    """
    This backend will poll multiple HTTP endpoints/services and return events
    the bus whenever something new happened. Supported types:
    :class:`platypush.backend.http.request.JsonHttpRequest` (for polling updates on
    a JSON endpoint), :class:`platypush.backend.http.request.rss.RssUpdates`
    (for polling updates on an RSS feed). Example configuration::

        backend.http.poll:
            requests:
                -
                    # Poll for updates on a JSON endpoint
                    method: GET
                    type: platypush.backend.http.request.JsonHttpRequest
                    args:
                        url: https://host.com/api/v1/endpoint
                        headers:
                            Token: TOKEN
                        params:
                            updatedSince: 1m
                        timeout: 5  # Times out after 5 seconds (default)
                    poll_seconds: 60  # Check for updates on this endpoint every 60 seconds (default)
                    path: ${response['items']}  # Path in the JSON to check for new items.
                                                # Python expressions are supported.
                                                # Note that 'response' identifies the JSON root.
                                                # Default value: JSON root.
                -
                    # Poll for updates on an RSS feed
                    type: platypush.backend.http.request.rss.RssUpdates
                    url: http://www.theguardian.com/rss/world
                    title: The Guardian - World News
                    poll_seconds: 120
                    max_entries: 10

    Triggers: an update event for the relevant HTTP source if it contains new items. For example:

        * :class:`platypush.message.event.http.rss.NewFeedEvent` if a feed contains new items
        * :class:`platypush.message.event.http.HttpEvent` if a JSON endpoint contains new items
    """

    def __init__(self, requests, *args, **kwargs):
        """
        :param requests: Configuration of the requests to make (see class description for examples)
        :type requests: dict
        """

        super().__init__(*args, **kwargs)
        self.requests = []

        for request in requests:
            if isinstance(request, dict):
                req_type = request['type']
                (module, name) = ('.'.join(req_type.split('.')[:-1]), req_type.split('.')[-1])
                module = importlib.import_module(module)
                request = getattr(module, name)(**request)
            elif not isinstance(request, HttpRequest):
                raise RuntimeError('Request should either be a dict or a ' +
                                   'HttpRequest object, {} found'.format(type(request)))

            request.bus = self.bus
            self.requests.append(request)

    def run(self):
        super().run()

        while not self.should_stop():
            for request in self.requests:
                if time.time() - request.last_request_timestamp > request.poll_seconds:
                    try:
                        request.execute()
                    except Exception as e:
                        self.logger.error('Error while executing request: {}'.format(request))
                        self.logger.exception(e)

            time.sleep(0.1)  # Prevent a tight loop


# vim:sw=4:ts=4:et:
