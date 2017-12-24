import logging

from .rule import EventRule

from platypush.config import Config
from platypush.message import Message
from platypush.message.request import Request

class EventProcessor(object):
    """ Event processor class. Checks an event against the configured
        rules and executes any matching event hooks """

    def __init__(self, hooks=Config.get_event_hooks(), **kwargs):
        """
        Params:
            hooks -- List of event hooks (default: any entry in the config
            named as event.hook.<hook_name> """

        self.hooks = {}
        for (name, hook) in hooks.items():
            self.hooks[name] = {
                'if': EventRule.build(hook['if'] if 'if' in hook else {}),
                'then': hook['then'],
            }

    def process_event(self, event):
        """ Processes an event and runs any matched hooks """

        matching_hooks = { name: hook['then'] for (name, hook) in self.hooks.items()
                           if event.matches_rule(hook['if']) }

        for (name, hook) in matching_hooks.items():
            logging.info('Running command {} triggered by matching event'
                         .format(name))

            # TODO Extend the request with the parameters coming from the event.
            # A hook should support a syntax like "playlist_id: $EVENT[playlist_id]"
            request = Request.build(hook)
            request.execute()


# vim:sw=4:ts=4:et:

