import logging
import sys

from ..hook import EventHook

from platypush.config import Config
from platypush.context import get_backend


class EventProcessor(object):
    """ Event processor class. Checks an event against the configured
        rules and executes any matching event hooks """

    def __init__(self, hooks=None, **kwargs):
        """
        Params:
            hooks -- List of event hooks (default: any entry in the config
            named as event.hook.<hook_name> """

        if hooks is None: hooks = Config.get_event_hooks()

        self.hooks = []
        for (name, hook) in hooks.items():
            h = EventHook.build(name=name, hook=hook)
            self.hooks.append(h)


    def notify_web_clients(self, event):
        backends = Config.get_backends()
        if 'http' not in backends: return

        backend = get_backend('http')
        if backend:
            backend.notify_web_clients(event)


    def process_event(self, event):
        """ Processes an event and runs the matched hooks with the highest score """

        self.notify_web_clients(event)
        matched_hooks = set(); priority_hooks = set()
        max_score = -sys.maxsize; max_prio = 0

        for hook in self.hooks:
            match = hook.matches_event(event)
            if match.is_match:
                if match.score > max_score:
                    matched_hooks = set((hook,))
                    max_score = match.score
                elif match.score == max_score:
                    matched_hooks.add(hook)

                if hook.priority > max_prio:
                    priority_hooks = set((hook,))
                elif hook.priority == max_prio and max_prio > 0:
                    priority_hooks.add(hook)

        matched_hooks.update(priority_hooks)
        for hook in matched_hooks:
            hook.run(event)


# vim:sw=4:ts=4:et:

