import pytest

from platypush.event.hook import EventCondition
from platypush.message.event.ping import PingEvent


condition = EventCondition.build({
    'type': 'platypush.message.event.ping.PingEvent',
    'message': 'This is (the)? answer: ${answer}'
})


def test_event_parse():
    """
    Test for the events/conditions matching logic.
    """
    message = "GARBAGE GARBAGE this is the answer: 42"
    event = PingEvent(message=message)
    result = event.matches_condition(condition)
    assert result.is_match
    assert 'answer' in result.parsed_args
    assert result.parsed_args['answer'] == '42'

    message = "what is not the answer? 43"
    event = PingEvent(message=message)
    result = event.matches_condition(condition)
    assert not result.is_match


if __name__ == '__main__':
    pytest.main()


# vim:sw=4:ts=4:et:
