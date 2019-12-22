import sys

from ..hook import EventHook

from platypush.config import Config
from platypush.context import get_backend
from platypush.message.event import Event


class EventProcessor(object):
    """ Event processor class. Checks an event against the configured
        rules and executes any matching event hooks """

    def __init__(self, hooks=None):
        """
        Params:
            hooks -- List of event hooks (default: any entry in the config
            named as event.hook.<hook_name> """

        if hooks is None:
            hooks = Config.get_event_hooks()

        self.hooks = []
        for (name, hook) in hooks.items():
            h = EventHook.build(name=name, hook=hook)
            self.hooks.append(h)

    @staticmethod
    def notify_web_clients(event):
        backends = Config.get_backends()
        if 'http' not in backends:
            return

        backend = get_backend('http')
        if backend:
            backend.notify_web_clients(event)

        backend = get_backend('websocket')
        if backend:
            backend.notify_web_clients(event)

    def process_event(self, event: Event):
        """ Processes an event and runs the matched hooks with the highest score """

        if not event.disable_web_clients_notification:
            self.notify_web_clients(event)

        matched_hooks = set()
        priority_hooks = set()
        max_score = -sys.maxsize
        max_priority = 0

        for hook in self.hooks:
            match = hook.matches_event(event)
            if match.is_match:
                if match.score > max_score:
                    matched_hooks = {hook}
                    max_score = match.score
                elif match.score == max_score:
                    matched_hooks.add(hook)

                if hook.priority > max_priority:
                    priority_hooks = {hook}
                elif hook.priority == max_priority and max_priority > 0:
                    priority_hooks.add(hook)

        matched_hooks.update(priority_hooks)
        for hook in matched_hooks:
            hook.run(event)


# vim:sw=4:ts=4:et:
