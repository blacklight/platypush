import importlib
import time

from platypush.bus import Bus
from platypush.backend import Backend
from platypush.backend.http.request import HttpRequest


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
                    url: https://hub-api.booking.com/v1/hotels/84326/reservations
                    headers:
                        X-Booking-Auth-Token: UXsYtIMJKCJB07/P/5Tz1iV8lzVY5kVVF0ZEnQRe+cg0
                    params:
                        updatedSince: 2018-01-09

                poll_seconds: 10  # Check for updates on this endpoint every 10 seconds (default: 60)
                timeout: 5  # Times out after 5 seconds (default)
    """

    def __init__(self, requests, *args, **kwargs):
        """
        Params:
            requests -- List/iterable of HttpRequest objects
        """

        super().__init__(*args, **kwargs)

        self.requests = []
        self.http_bus = Bus()

        for request in requests:
            if isinstance(request, dict):
                type = request['type']
                (module, name) = ('.'.join(type.split('.')[:-1]), type.split('.')[-1])
                module = importlib.import_module(module)
                request = getattr(module, name)(bus=self.http_bus, **request)
            elif isinstance(request, HttpRequest):
                request.bus = self.http_bus
            else:
                raise RuntimeError('Request should either be a dict or a ' +
                                   'HttpRequest object, {} found'.format(type(request)))

            self.requests.append(request)


    def run(self):
        super().run()

        while not self.should_stop():
            for request in self.requests:
                if not request.is_alive() and (
                        request.last_call_timestamp is None or
                        time.time() - request.last_call_timestamp > request.poll_seconds):
                    response = request.execute()
                    print('**** RESPONSE: {}'.format(response))

            time.sleep(0.1)

    def send_message(self, msg):
        self.http_bus.post(msg)


# vim:sw=4:ts=4:et:

