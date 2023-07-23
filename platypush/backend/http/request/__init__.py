import logging
import re
from threading import Thread
import time

import requests
from frozendict import frozendict

from platypush.message.event.http import HttpEvent


class HttpRequest:
    """
    Backend used for polling HTTP resources.
    """

    poll_seconds = 60
    timeout = 5

    class HttpRequestArguments:
        """
        Models the properties of an HTTP request.
        """

        def __init__(self, url, *args, method='get', **kwargs):
            self.method = method.lower()
            self.url = url
            self.args = args
            self.kwargs = kwargs

    def __init__(
        self, args, bus=None, poll_seconds=None, timeout=None, skip_first_call=True, **_
    ):
        super().__init__()

        self.poll_seconds = poll_seconds or self.poll_seconds
        self.timeout = timeout or self.timeout
        self.bus = bus
        self.skip_first_call = skip_first_call
        self.last_request_timestamp = 0
        self.logger = logging.getLogger('platypush')

        if isinstance(args, self.HttpRequestArguments):
            self.args = args
        elif isinstance(args, dict):
            self.args = self.HttpRequestArguments(**args)
        else:
            raise RuntimeError('{} is neither a dictionary nor an HttpRequest')

        if 'timeout' not in self.args.kwargs:
            self.args.kwargs['timeout'] = self.timeout

        self.request_args = {
            'method': self.args.method,
            'url': self.args.url,
            **self.args.kwargs,
        }

    def execute(self):
        def _thread_func():
            is_first_call = self.last_request_timestamp == 0
            self.last_request_timestamp = time.time()

            try:
                method = getattr(requests, self.args.method.lower())
                response = method(self.args.url, *self.args.args, **self.args.kwargs)
                new_items = self.get_new_items(response)

                if isinstance(new_items, HttpEvent):
                    event = new_items
                    new_items = event.args['response']
                else:
                    event = HttpEvent(dict(self), new_items)

                if (
                    new_items
                    and self.bus
                    and (
                        not self.skip_first_call
                        or (self.skip_first_call and not is_first_call)
                    )
                ):
                    self.bus.post(event)

                response.raise_for_status()
            except Exception as e:
                self.logger.exception(e)
                self.logger.warning(
                    'Encountered an error while retrieving %s: %s', self.args.url, e
                )

        Thread(target=_thread_func, name='HttpPoll').start()

    def get_new_items(self, response):
        """Gets new items out of a response"""
        raise NotImplementedError(
            "get_new_items must be implemented in a derived class"
        )

    def __iter__(self):
        """
        :return: The ``request_args`` as key-value pairs.
        """
        for key, value in self.request_args.items():
            yield key, value


class JsonHttpRequest(HttpRequest):
    """
    Specialization of the HttpRequest class for JSON requests.
    """

    def __init__(self, *args, path=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.path = path
        self.seen_entries = set()

    def get_new_items(self, response):
        response = response.json()
        new_entries = []

        if self.path:
            m = re.match(r'\${\s*(.*)\s*}', self.path)
            if m:
                response = eval(m.group(1))  # pylint: disable=eval-used

        for entry in response:
            flattened_entry = deep_freeze(entry)
            if flattened_entry not in self.seen_entries:
                new_entries.append(entry)
            self.seen_entries.add(flattened_entry)

        return new_entries


def deep_freeze(x):
    """
    Deep freezes a Python object - works for strings, dictionaries, sets and
    iterables.
    """

    if isinstance(x, str) or not hasattr(x, "__len__"):
        return x
    if hasattr(x, "keys") and hasattr(x, "values"):
        return frozendict({deep_freeze(k): deep_freeze(v) for k, v in x.items()})
    if hasattr(x, "__getitem__"):
        return tuple(map(deep_freeze, x))

    return frozenset(map(deep_freeze, x))


# vim:sw=4:ts=4:et:
