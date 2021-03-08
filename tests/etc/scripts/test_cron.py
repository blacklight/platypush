import datetime

from platypush.cron import cron

from tests.test_cron import tmp_files, tmp_files_ready, \
    test_timeout, expected_cron_file_content

# Prepare a cronjob that should start test_timeout/2 seconds from the application start
cron_time = datetime.datetime.now() + datetime.timedelta(seconds=test_timeout/2)
cron_expr = '{min} {hour} {day} {month} * {sec}'.format(
    min=cron_time.minute, hour=cron_time.hour, day=cron_time.day,
    month=cron_time.month, sec=cron_time.second)


@cron(cron_expr)
def cron_test(**_):
    """
    Simple cronjob that awaits for ``../test_cron.py`` to be ready and writes the expected
    content to the monitored temporary file.
    """
    files_ready = tmp_files_ready.wait(timeout=test_timeout)
    assert files_ready, \
        'The test did not prepare the temporary files within {} seconds'.format(test_timeout)

    with open(tmp_files[0], 'w') as f:
        f.write(expected_cron_file_content)
