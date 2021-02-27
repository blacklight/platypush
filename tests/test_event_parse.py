import os
import unittest

from platypush.event.hook import EventCondition
from platypush.message.event.ping import PingEvent

from . import BaseTest, conf_dir


class TestEventParse(BaseTest):
    config_file = os.path.join(conf_dir, 'test_http_config.yaml')
    condition = EventCondition.build({
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
