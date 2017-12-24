import logging

from ..hook import EventHook

from platypush.config import Config


class EventProcessor(object):
    """ Event processor class. Checks an event against the configured
        rules and executes any matching event hooks """

    def __init__(self, hooks=Config.get_event_hooks(), **kwargs):
        """
        Params:
            hooks -- List of event hooks (default: any entry in the config
            named as event.hook.<hook_name> """

        self.hooks = []
        for (name, hook) in hooks.items():
            h = EventHook.build(name=name, hook=hook)
            self.hooks.append(h)


    def process_event(self, event):
        """ Processes an event and runs any matched hooks """

        matched_hooks = []
        max_score = 0

        for hook in self.hooks:
            match = hook.matches_event(event)
            if match.is_match:
                if match.score > max_score:
                    matched_hooks = [hook]
                elif match.score == max_score:
                    matched_hooks.append(hook)

        for hook in matched_hooks:
            hook.run(event)


# vim:sw=4:ts=4:et:

