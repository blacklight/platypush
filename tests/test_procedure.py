import os
import pytest
import tempfile
import time

from platypush.message.event.custom import CustomEvent

from .utils import register_user, send_request


@pytest.fixture(scope='module', autouse=True)
def user(*_):
    register_user()


@pytest.fixture(scope='module')
def tmp_file(*_):
    tmp_file = tempfile.NamedTemporaryFile(prefix='platypush-test-procedure-', suffix='.txt', delete=False)
    yield tmp_file
    if os.path.isfile(tmp_file.name):
        os.unlink(tmp_file.name)


def check_file_content(expected_content: str, tmp_file):
    assert os.path.isfile(tmp_file.name), 'The expected output file was not created'
    with open(tmp_file.name, 'r') as f:
        content = f.read()

    assert content == expected_content, 'The output file did not contain the expected text'


def test_procedure_call(tmp_file):
    """
    Test the result of a procedure invoked directly over HTTP.
    """
    output_text = 'Procedure test'
    send_request(
        action='procedure.write_file',
        args={
            'file': tmp_file.name,
            'content': output_text,
        })

    check_file_content(expected_content=output_text, tmp_file=tmp_file)


def test_procedure_from_event(app, tmp_file):
    """
    Test the result of a procedure triggered by an event.
    """
    output_text = 'Procedure from event test'
    event_type = 'platypush_test_procedure_from_event'
    # noinspection PyUnresolvedReferences
    app.bus.post(CustomEvent(subtype=event_type, file=tmp_file.name, content=output_text))
    time.sleep(2)
    check_file_content(expected_content=output_text, tmp_file=tmp_file)


# vim:sw=4:ts=4:et:
