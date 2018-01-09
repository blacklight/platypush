import json
import requests

from threading import Thread

from platypush.message.response import Response

from .. import Backend


class HttpPollBackend(Backend):
    """
    This backend will poll multiple HTTP endpoints/services and return events
    the bus whenever something new happened. Example configuration:

    backend.http.poll:
        services:
            -
                type: platypush.backend.http.service.ota.booking.GetReservations
                args:
                    token: YOUR_TOKEN
                poll_seconds: 10  # Check for updates on this endpoint every 10 seconds
                limit: 5  # Return the first 5 (new) results (default: all)
    """

    def __init__(self, services, *args, **kwargs):
        """
        Params:
            services -- List/iterable of HttpService objects
        """

        super().__init__(*args, **kwargs)
        self.services = services


    def run(self):
        super().run()

    def send_message(self, msg):
        pass

    def on_stop(self):
        pass

    def stop(self):
        super().stop()


# vim:sw=4:ts=4:et:

