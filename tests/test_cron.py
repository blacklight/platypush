import queue
import pytest
import time

test_timeout = 10
cron_queue = queue.Queue()


def _test_cron_queue(expected_msg: str):
    msg = None
    test_start = time.time()
    while time.time() - test_start <= test_timeout and msg != expected_msg:
        try:
            msg = cron_queue.get(block=True, timeout=test_timeout)
        except queue.Empty:
            break

    assert msg == expected_msg, 'The expected cronjob has not been executed'


def test_cron_execution():
    """
    Test that the cronjob in ``../etc/scripts/test_cron.py`` runs successfully.
    """
    _test_cron_queue('cron_test')


if __name__ == '__main__':
    pytest.main()


# vim:sw=4:ts=4:et:
