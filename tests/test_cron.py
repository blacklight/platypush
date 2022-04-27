import datetime
import queue
import pytest
import time

from dateutil.tz import gettz
from mock import patch

test_timeout = 10
cron_queue = queue.Queue()


class MockDatetime(datetime.datetime):
    timedelta = datetime.timedelta()

    @classmethod
    def now(cls):
        return super().now(tz=gettz()) + cls.timedelta


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


def test_cron_execution_upon_system_clock_change():
    """
    Test that the cronjob runs at the right time even upon DST or other
    system clock changes.
    """
    # Mock datetime.datetime with a class that has overridable timedelta
    patcher = patch('datetime.datetime', MockDatetime)

    try:
        patcher.start()
        time.sleep(1)
        # Simulate a +1hr shift on the system clock
        MockDatetime.timedelta = datetime.timedelta(hours=1)
        time.sleep(1)
    finally:
        patcher.stop()

    # Ensure that the cronjob that was supposed to run in an hour is now running
    _test_cron_queue('cron_1hr_test')


if __name__ == '__main__':
    pytest.main()


# vim:sw=4:ts=4:et:
