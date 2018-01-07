from .context import platypush

import unittest

from platypush.event.hook import EventHook, EventCondition, EventAction
from platypush.message.event.ping import PingEvent

class TestEventParse(unittest.TestCase):
    def setUp(self):
        self.condition = EventCondition.build({
            'type': 'platypush.message.event.ping.PingEvent',
            'message': 'This is (the)? answer: ${answer}'
        })

    def test_event_parse(self):
        message = "GARBAGE GARBAGE this is the answer: 42"
        event = PingEvent(message=message)
        result = event.matches_condition(self.condition)
        self.assertTrue(result.is_match)
        self.assertTrue('answer' in result.parsed_args)
        self.assertEqual(result.parsed_args['answer'], '42')

        message = "what is not the answer? 43"
        event = PingEvent(message=message)
        result = event.matches_condition(self.condition)
        self.assertFalse(result.is_match)


if __name__ == '__main__':
    unittest.main()

# vim:sw=4:ts=4:et:

