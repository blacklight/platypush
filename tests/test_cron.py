import queue
import pytest
import time

test_timeout = 15  # Increased timeout to be more forgiving
cron_queue = queue.Queue()


def _test_cron_queue(expected_msg: str):
    msg = None
    test_start = time.time()
    # Use shorter polling intervals for better responsiveness
    poll_timeout = 1.0

    while time.time() - test_start <= test_timeout and msg != expected_msg:
        try:
            msg = cron_queue.get(block=True, timeout=poll_timeout)
            if msg == expected_msg:
                break
        except queue.Empty:
            continue  # Keep polling until timeout

    assert (
        msg == expected_msg
    ), f'The expected cronjob has not been executed. Got: {msg}, Expected: {expected_msg}'


def test_cron_execution():
    """
    Test that the cronjob in ``../etc/scripts/test_cron.py`` runs successfully.
    """
    _test_cron_queue('cron_test')


if __name__ == '__main__':
    pytest.main()


# vim:sw=4:ts=4:et:
