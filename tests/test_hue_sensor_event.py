from unittest.mock import MagicMock, patch

from platypush.message.event.hue import HueSensorEvent
from platypush.plugins.light.hue import LightHuePlugin


def _plugin() -> LightHuePlugin:
    # Bypass __init__ - it would try to connect to a real bridge
    return LightHuePlugin.__new__(LightHuePlugin)


def _sensor(state: dict, **kwargs) -> dict:
    return {
        'name': 'Bathroom Dimmer',
        'type': 'ZLLSwitch',
        'uniqueid': '00:11:22:33:44:55:66:77-88-99',
        'state': state,
        **kwargs,
    }


def _posted_events(plugin, sensors_new, sensors_prev):
    bus = MagicMock()
    with patch('platypush.plugins.light.hue.get_bus', return_value=bus):
        plugin._post_sensor_events(
            sensors_new, sensors_prev
        )  # pylint: disable=protected-access

    return [call.args[0] for call in bus.post.call_args_list]


def test_sensor_event_args():
    event = HueSensorEvent(
        sensor_id=21,
        sensor_name='Bathroom Dimmer',
        sensor_type='ZLLSwitch',
        unique_id='00:11:22:33:44:55:66:77-88-99',
        state={'buttonevent': 1002},
        button=1,
        button_action='short_release',
        plugin_name='light.hue',
    )

    assert event.args['sensor_id'] == 21
    assert event.args['sensor_name'] == 'Bathroom Dimmer'
    assert event.args['sensor_type'] == 'ZLLSwitch'
    assert event.args['unique_id'] == '00:11:22:33:44:55:66:77-88-99'
    assert event.args['state'] == {'buttonevent': 1002}
    assert event.args['button'] == 1
    assert event.args['button_action'] == 'short_release'
    assert event.args['plugin_name'] == 'light.hue'


def test_decode_button_event():
    decode = LightHuePlugin._decode_button_event  # pylint: disable=protected-access

    assert decode(1000) == (1, 'initial_press')
    assert decode(1001) == (1, 'hold')
    assert decode(2002) == (2, 'short_release')
    assert decode(4003) == (4, 'long_release')
    # Non-standard buttonevents (e.g. Hue Tap) aren't decoded
    assert decode(16) is None
    assert decode(0) is None
    assert decode(None) is None
    assert decode('1002') is None


def test_no_event_on_unchanged_state():
    sensor = _sensor({'buttonevent': 1002, 'lastupdated': '2026-10-24T10:00:00'})
    events = _posted_events(_plugin(), {'21': sensor}, {'21': sensor})
    assert not events


def test_button_press_event():
    prev = _sensor({'buttonevent': 1002, 'lastupdated': '2026-10-24T10:00:00'})
    new = _sensor({'buttonevent': 2000, 'lastupdated': '2026-10-24T10:00:01'})

    events = _posted_events(_plugin(), {'21': new}, {'21': prev})

    assert len(events) == 1
    event = events[0]
    assert isinstance(event, HueSensorEvent)
    assert event.args['sensor_name'] == 'Bathroom Dimmer'
    assert event.args['button'] == 2
    assert event.args['button_action'] == 'initial_press'


def test_repeated_button_press_still_fires():
    # Pressing the same button twice only changes `lastupdated` - the event
    # should still fire
    prev = _sensor({'buttonevent': 1002, 'lastupdated': '2026-10-24T10:00:00'})
    new = _sensor({'buttonevent': 1002, 'lastupdated': '2026-10-24T10:00:01'})

    events = _posted_events(_plugin(), {'21': new}, {'21': prev})

    assert len(events) == 1
    assert events[0].args['button'] == 1
    assert events[0].args['button_action'] == 'short_release'


def test_non_switch_sensor_event():
    prev = _sensor(
        {'presence': False, 'lastupdated': '2026-10-24T10:00:00'},
        name='Hallway Sensor',
        type='ZLLPresence',
    )
    new = _sensor(
        {'presence': True, 'lastupdated': '2026-10-24T10:00:01'},
        name='Hallway Sensor',
        type='ZLLPresence',
    )

    events = _posted_events(_plugin(), {'7': new}, {'7': prev})

    assert len(events) == 1
    event = events[0]
    assert event.args['sensor_name'] == 'Hallway Sensor'
    assert event.args['sensor_type'] == 'ZLLPresence'
    assert event.args['state']['presence'] is True
    assert 'button' not in event.args
    assert 'button_action' not in event.args
