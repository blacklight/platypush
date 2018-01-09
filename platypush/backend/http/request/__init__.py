import copy
import json
import re
import requests
import time

from frozendict import frozendict
from threading import Thread

from platypush.message.response import Response

class HttpRequest(Thread):
    poll_seconds = 60
    timeout = 5
    bus = None
    last_call_timestamp = None


    class HttpRequestArguments(object):
        def __init__(self, url, method='get', *args, **kwargs):
            self.method = method.lower()
            self.url = url
            self.args = args
            self.kwargs = kwargs


    def __init__(self, args, poll_seconds=None, timeout=None, bus=None, **kwargs):
        super().__init__()

        self.poll_seconds = poll_seconds or self.poll_seconds
        self.timeout = timeout or self.timeout
        self.bus = bus or self.bus

        if isinstance(args, self.HttpRequestArguments):
            self.args = args
        elif isinstance(args, dict):
            self.args = self.HttpRequestArguments(**args)
        else:
            raise RuntimeError('{} is neither a dictionary nor an HttpRequest')


    def execute(self):
        self.last_call_timestamp = time.time()

        method = getattr(requests, self.args.method.lower())
        response = method(self.args.url, *self.args.args, **self.args.kwargs)
        response.raise_for_status()
        return response


class JsonHttpRequest(HttpRequest):
    def __init__(self, path=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.path = path
        self.seen_entries = set()


    def execute(self):
        is_first_call = self.last_call_timestamp is None
        response = super().execute().json()
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

