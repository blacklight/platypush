import os
import pytest
import tempfile
import threading
import time

tmp_files = []
tmp_files_ready = threading.Event()
test_timeout = 10
expected_cron_file_content = 'The cronjob ran successfully!'


@pytest.fixture(scope='module', autouse=True)
def tmp_file(*_):
    tmp_file = tempfile.NamedTemporaryFile(prefix='platypush-test-cron-',
                                           suffix='.txt', delete=False)
    tmp_files.append(tmp_file.name)
    tmp_files_ready.set()
    yield tmp_file.name

    for f in tmp_files:
        if os.path.isfile(f):
            os.unlink(f)


def test_cron_execution(tmp_file):
    """
    Test that the cronjob in ``../etc/scripts/test_cron.py`` runs successfully.
    """
    actual_cron_file_content = None
    test_start = time.time()

    while actual_cron_file_content != expected_cron_file_content and \
            time.time() - test_start < test_timeout:
        with open(tmp_file, 'r') as f:
            actual_cron_file_content = f.read()
        time.sleep(0.5)

    assert actual_cron_file_content == expected_cron_file_content, \
        'cron_test failed to run within {} seconds'.format(test_timeout)


if __name__ == '__main__':
    pytest.main()


# vim:sw=4:ts=4:et:
