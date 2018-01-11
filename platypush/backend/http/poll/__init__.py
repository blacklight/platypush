import importlib
import time

from threading import Thread

from platypush.bus import Bus
from platypush.backend import Backend
from platypush.backend.http.request import HttpRequest
from platypush.message.request import Request


class HttpPollBackend(Backend):
    """
    This backend will poll multiple HTTP endpoints/services and return events
    the bus whenever something new happened. Example configuration:

    backend.http.poll:
        requests:
            -
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
    """

    def __init__(self, requests, *args, **kwargs):
        """
        Params:
            requests -- List/iterable of HttpRequest objects
        """

        super().__init__(*args, **kwargs)
        self.requests = []

        for request in requests:
            if isinstance(request, dict):
                type = request['type']
                (module, name) = ('.'.join(type.split('.')[:-1]), type.split('.')[-1])
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
                    request.execute()

            time.sleep(0.1)  # Prevent a tight loop


    def send_message(self, msg):
        pass


# vim:sw=4:ts=4:et:

