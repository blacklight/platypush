import logging
import sys

from ..hook import EventHook

from platypush.config import Config


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


    def process_event(self, event):
        """ Processes an event and runs the matched hooks with the highest score """

        matched_hooks = set(); priority_hooks = set()
        max_score = -sys.maxsize; max_prio = 0

        for hook in self.hooks:
            match = hook.matches_event(event)
            if match.is_match:
                if match.score > max_score:
                    matched_hooks = set((hook,))
                elif match.score == max_score:
                    matched_hooks.add(hook)

                if hook.priority > max_prio:
                    priority_hooks = set((hook,))
                elif hook.priority == max_prio:
                    priority_hooks.add(hook)

        matched_hooks.update(priority_hooks)
        for hook in matched_hooks:
            hook.run(event)


# vim:sw=4:ts=4:et:

