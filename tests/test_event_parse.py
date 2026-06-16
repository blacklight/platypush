import pytest

from platypush.event.hook import EventCondition
from platypush.message.event.assistant import SpeechRecognizedEvent
from platypush.message.event.ping import PingEvent


def test_event_parse():
    """
    Test for the events/conditions matching logic.
    """
    condition = EventCondition.build(
        {
            'type': 'platypush.message.event.ping.PingEvent',
            'message': 'This is a test message',
        }
    )

    event = PingEvent(message=condition.args['message'])
    result = event.matches_condition(condition)
    if not (result.is_match):
        raise AssertionError

    event = PingEvent(message="This is not a test message")
    result = event.matches_condition(condition)
    if result.is_match:
        raise AssertionError


def test_nested_event_condition():
    """
    Verify that nested event conditions work as expected.
    """
    condition = EventCondition.build(
        {
            'type': 'platypush.message.event.ping.PingEvent',
            'message': {
                'foo': 'bar',
            },
        }
    )

    event = PingEvent(
        message={
            'foo': 'bar',
            'baz': 'clang',
        }
    )

    if not (event.matches_condition(condition).is_match):
        raise AssertionError

    event = PingEvent(
        message={
            'something': 'else',
        }
    )

    if event.matches_condition(condition).is_match:
        raise AssertionError

    event = PingEvent(
        message={
            'foo': 'baz',
        }
    )

    if event.matches_condition(condition).is_match:
        raise AssertionError


def test_speech_recognized_event_parse():
    """
    Test the event parsing and text extraction logic for the
    SpeechRecognizedEvent.
    """
    condition = EventCondition.build(
        {
            'type': 'platypush.message.event.assistant.SpeechRecognizedEvent',
            'phrase': 'This is (the)? answer: ${answer}',
        }
    )

    event = SpeechRecognizedEvent(phrase="GARBAGE GARBAGE this is the answer: 42")
    result = event.matches_condition(condition)
    if not (result.is_match):
        raise AssertionError
    if not ('answer' in result.parsed_args):
        raise AssertionError
    if not (result.parsed_args['answer'] == '42'):
        raise AssertionError

    event = SpeechRecognizedEvent(phrase="what is not the answer? 43")
    result = event.matches_condition(condition)
    if result.is_match:
        raise AssertionError


def test_condition_with_relational_operators():
    """
    Test relational operators used in event conditions.
    """
    # Given: A condition with a relational operator.
    condition = EventCondition.build(
        {
            'type': 'platypush.message.event.ping.PingEvent',
            'message': {'foo': {'$gt': 25}},
        }
    )

    # When: An event with a value greater than 25 is received.
    event = PingEvent(message={'foo': 26})

    # Then: The condition is matched.
    if not (event.matches_condition(condition).is_match):
        raise AssertionError

    # When: An event with a value lower than 25 is received.
    event = PingEvent(message={'foo': 24})

    # Then: The condition is not matched.
    if event.matches_condition(condition).is_match:
        raise AssertionError


def test_filter_with_regex_condition():
    """
    Test an event matcher with a regex filter on an attribute.
    """
    # Given: A condition with a regex filter.
    condition = EventCondition.build(
        {
            'type': 'platypush.message.event.ping.PingEvent',
            'message': {'foo': {'$regex': '^ba[rz]'}},
        }
    )

    # When: An event with a matching string is received.
    event = PingEvent(message={'foo': 'bart'})

    # Then: The condition is matched.
    if not (event.matches_condition(condition).is_match):
        raise AssertionError

    # When: An event with a non-matching string is received.
    event = PingEvent(message={'foo': 'back'})

    # Then: The condition is not matched.
    if event.matches_condition(condition).is_match:
        raise AssertionError


if __name__ == '__main__':
    pytest.main()


# vim:sw=4:ts=4:et:
