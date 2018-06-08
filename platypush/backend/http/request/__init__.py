import copy
import importlib
import json
import logging
import re
import requests
import time

from datetime import date
from frozendict import frozendict
from threading import Thread

from platypush.message.event.http import HttpEvent

class HttpRequest(object):
    poll_seconds = 60
    timeout = 5


    class HttpRequestArguments(object):
        def __init__(self, url, method='get', *args, **kwargs):
            self.method = method.lower()
            self.url = url
            self.args = args
            self.kwargs = kwargs


    def __init__(self, args, bus=None, poll_seconds=None, timeout=None,
                 skip_first_call=True, **kwargs):
        super().__init__()

        self.poll_seconds = poll_seconds or self.poll_seconds
        self.timeout = timeout or self.timeout
        self.bus = bus
        self.skip_first_call = skip_first_call
        self.last_request_timestamp = 0
        self.logger = logging.getLogger(__name__)

        if isinstance(args, self.HttpRequestArguments):
            self.args = args
        elif isinstance(args, dict):
            self.args = self.HttpRequestArguments(**args)
        else:
            raise RuntimeError('{} is neither a dictionary nor an HttpRequest')

        if 'timeout' not in self.args.kwargs:
            self.args.kwargs['timeout'] = self.timeout

        self.request_args = {
            'method': self.args.method, 'url': self.args.url, **self.args.kwargs
        }


    def execute(self):
        def _thread_func():
            is_first_call = self.last_request_timestamp == 0
            self.last_request_timestamp = time.time()

            method = getattr(requests, self.args.method.lower())
            response = method(self.args.url, *self.args.args, **self.args.kwargs)
            new_items = self.get_new_items(response)

            if isinstance(new_items, HttpEvent):
                event = new_items
                new_items = event.args['response']
            else:
                event = HttpEvent(dict(self), new_items)

            if new_items and self.bus:
                if not self.skip_first_call or (
                        self.skip_first_call and not is_first_call):
                    self.bus.post(event)

            response.raise_for_status()

        Thread(target=_thread_func).start()


    def get_new_items(self, response):
        """ Gets new items out of a response """
        raise("get_new_items must be implemented in a derived class")


    def __iter__(self):
        for (key, value) in self.request_args.items():
            yield (key, value)


class JsonHttpRequest(HttpRequest):
    def __init__(self, path=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.path = path
        self.seen_entries = set()


    def get_new_items(self, response):
        response = response.json()
        new_entries = []

        if self.path:
            m = re.match('\$\{\s*(.*)\s*\}', self.path)
            response = eval(m.group(1))

        for entry in response:
            flattened_entry = deep_freeze(entry)
            if flattened_entry not in self.seen_entries:
                new_entries.append(entry)
            self.seen_entries.add(flattened_entry)

        return new_entries


def deep_freeze(x):
    if isinstance(x, str) or not hasattr(x, "__len__") :
        return x
    if hasattr(x, "keys") and hasattr(x, "values") :
        return frozendict({deep_freeze(k) : deep_freeze(v) for k,v in x.items()})
    if hasattr(x, "__getitem__") :
        return tuple(map(deep_freeze, x))

    return frozenset(map(deep_freeze,x))


# vim:sw=4:ts=4:et:

