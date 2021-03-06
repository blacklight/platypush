import os
import pytest
import tempfile
import time

from platypush.message.event.custom import CustomEvent

from .utils import register_user, send_request

tmp_files = []


@pytest.fixture(scope='module', autouse=True)
def user(*_):
    register_user()


@pytest.fixture(scope='module', autouse=True)
def tmp_file(*_):
    n_files = 2
    for _ in range(n_files):
        tmp_file = tempfile.NamedTemporaryFile(prefix='platypush-test-procedure-', suffix='.txt', delete=False)
        tmp_files.append(tmp_file.name)

    yield

    for f in tmp_files:
        if os.path.isfile(f):
            os.unlink(f)


def check_file_content(expected_content: str, tmp_file: str, timeout: int = 10):
    error = None
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            assert os.path.isfile(tmp_file), 'The expected output file was not created'
            with open(tmp_file, 'r') as f:
                content = f.read()

            assert content == expected_content, 'The output file did not contain the expected text'
            error = None
            break
        except Exception as e:
            error = e

    if error:
        raise error


def test_procedure_call(base_url):
    """
    Test the result of a procedure invoked directly over HTTP.
    """
    output_text = 'Procedure test'
    send_request(
        action='procedure.write_file',
        args={
            'file': tmp_files[0],
            'content': output_text,
        })

    check_file_content(expected_content=output_text, tmp_file=tmp_files[0])


def test_procedure_from_event(app, base_url):
    """
    Test the result of a procedure triggered by an event.
    """
    output_text = 'Procedure from event test'
    event_type = 'test_procedure'
    # noinspection PyUnresolvedReferences
    app.bus.post(CustomEvent(subtype=event_type, file=tmp_files[1], content=output_text))
    check_file_content(expected_content=output_text, tmp_file=tmp_files[1])


if __name__ == '__main__':
    pytest.main()


# vim:sw=4:ts=4:et:
