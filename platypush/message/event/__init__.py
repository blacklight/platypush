import copy
import json
import random
import re
import threading

from datetime import date

from platypush.config import Config
from platypush.message import Message
from platypush.utils import get_event_class_by_type

class Event(Message):
    """ Event message class """

    def __init__(self, target=None, origin=None, id=None, **kwargs):
        """
        Params:
            target  -- Target node [String]
            origin  -- Origin node (default: current node) [String]
            id      -- Event ID (default: auto-generated)
            kwargs  -- Additional arguments for the event [kwDict]
        """

        self.id = id if id else self._generate_id()
        self.target = target if target else Config.get('device_id')
        self.origin = origin if origin else Config.get('device_id')
        self.type = '{}.{}'.format(self.__class__.__module__,
                                   self.__class__.__name__)
        self.args = kwargs

    @classmethod
    def build(cls, msg):
        """ Builds an event message from a JSON UTF-8 string/bytearray, a
        dictionary, or another Event """

        msg = super().parse(msg)
        event_type = msg['args'].pop('type')
        event_class = get_event_class_by_type(event_type)

        args = msg['args'] if 'args' in msg else {}
        args['id'] = msg['id'] if 'id' in msg else cls._generate_id()
        args['target'] = msg['target'] if 'target' in msg else Config.get('device_id')
        args['origin'] = msg['origin'] if 'origin' in msg else Config.get('device_id')
        return event_class(**args)


    @staticmethod
    def _generate_id():
        """ Generate a unique event ID """
        id = ''
        for i in range(0,16):
            id += '%.2x' % random.randint(0, 255)
        return id


    def matches_condition(self, condition):
        """
        If the event matches an event condition, it will return an EventMatchResult
        Params:
            -- condition -- The platypush.event.hook.EventCondition object
        """

        result = EventMatchResult(is_match=False, parsed_args=self.args)
        match_scores = []

        if not isinstance(self, condition.type): return result

        for (attr, value) in condition.args.items():
            if attr not in self.args:
                return result

            if isinstance(self.args[attr], str):
                arg_result = self._matches_argument(argname=attr, condition_value=value)

                if arg_result.is_match:
                    match_scores.append(arg_result.score)
                    for (parsed_arg, parsed_value) in arg_result.parsed_args.items():
                        result.parsed_args[parsed_arg] = parsed_value
                else:
                    return result
            elif self.args[attr] != value:
                # TODO proper support for list and dictionary matches
                return result

        result.is_match = True
        if match_scores:
            result.score = sum(match_scores) / float(len(match_scores))

        return result


    def _matches_argument(self, argname, condition_value):
        """
        Returns an EventMatchResult if the event argument [argname] matches
        [condition_value].

        - Example:
            - self.args = {
                'phrase': 'Hey dude turn on the living room lights'
            }

            - self._matches_argument(argname='phrase', condition_value='Turn on the ${lights} lights')
              will return EventMatchResult(is_match=True, parsed_args={ 'lights': 'living room' })

            - self._matches_argument(argname='phrase', condition_value='Turn off the ${lights} lights')
              will return EventMatchResult(is_match=False, parsed_args={})
        """

        result = EventMatchResult(is_match=False)
        event_tokens = re.split('\s+', self.args[argname].strip().lower())
        condition_tokens = re.split('\s+', condition_value.strip().lower())

        while event_tokens and condition_tokens:
            event_token = event_tokens[0]
            condition_token = condition_tokens[0]

            if event_token == condition_token:
                event_tokens.pop(0)
                condition_tokens.pop(0)
                result.score += 1.5
            elif re.search(condition_token, event_token):
                m = re.search('({})'.format(condition_token), event_token)
                if m.group(1):
                    event_tokens.pop(0)
                    result.score += 1.25

                condition_tokens.pop(0)
            else:
                m = re.match('[^\\\]*\${(.+?)}', condition_token)
                if m:
                    argname = m.group(1)
                    if argname not in result.parsed_args:
                        result.parsed_args[argname] = event_token
                        result.score += 1.0
                    else:
                        result.parsed_args[argname] += ' ' + event_token


                    if (len(condition_tokens) == 1 and len(event_tokens) == 1) \
                            or (len(event_tokens) > 1 and len(condition_tokens) > 1 \
                            and event_tokens[1] == condition_tokens[1]):
                        # Stop appending tokens to this argument, as the next
                        # condition will be satisfied as well
                        condition_tokens.pop(0)

                    event_tokens.pop(0)
                else:
                    result.score -= 1.0
                    event_tokens.pop(0)

        # It's a match if all the tokens in the condition string have been satisfied
        result.is_match = len(condition_tokens) == 0
        return result


    def __str__(self):
        """
        Overrides the str() operator and converts
        the message into a UTF-8 JSON string
        """

        args = copy.deepcopy(self.args)
        flatten(args)

        return json.dumps({
            'type'     : 'event',
            'target'   : self.target,
            'origin'   : self.origin if hasattr(self, 'origin') else None,
            'id'       : self.id if hasattr(self, 'id') else None,
            'args'     : {
                'type' : self.type,
                **args
            },
        })


class EventMatchResult(object):
    """ When comparing an event against an event condition, you want to
        return this object. It contains the match status (True or False),
        any parsed arguments, and a match_score that identifies how "strong"
        the match is - in case of multiple event matches, the ones with the
        highest score will win """

    def __init__(self, is_match, score=0, parsed_args=None):
        self.is_match = is_match
        self.score = score
        self.parsed_args = {} if not parsed_args else parsed_args


# XXX Should be a stop Request, not an Event
class StopEvent(Event):
    """ StopEvent message. When received on a Bus, it will terminate the
    listening thread having the specified ID. Useful to keep listeners in
    sync and make them quit when the application terminates """

    def __init__(self, target, origin, thread_id, id=None, **kwargs):
        """ Constructor.
        Params:
            target    -- Target node
            origin    -- Origin node
            thread_id -- thread_iden() to be terminated if listening on the bus
            id        -- Event ID (default: auto-generated)
            kwargs    -- Extra key-value arguments
        """

        super().__init__(target=target, origin=origin, id=id,
                         thread_id=thread_id, **kwargs)

    def targets_me(self):
        """ Returns true if the stop event is for the current thread """
        return self.args['thread_id'] == threading.get_ident()


def flatten(args):
    if isinstance(args, dict):
        for (key,value) in args.items():
            if isinstance(value, date):
                args[key] = value.isoformat()
            elif isinstance(value, dict) or isinstance(value, list):
                flatten(args[key])
    elif isinstance(args, list):
        for i in range(0,len(args)):
            if isinstance(args[i], date):
                args[i] = value.isoformat()
            elif isinstance(args[i], dict) or isinstance(args[i], list):
                flatten(args[i])


# vim:sw=4:ts=4:et:

