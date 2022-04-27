import datetime

from platypush.cron import cron

from tests.test_cron import test_timeout, cron_queue


def make_cron_expr(cron_time: datetime.datetime):
    return '{min} {hour} {day} {month} * {sec}'.format(
        min=cron_time.minute,
        hour=cron_time.hour,
        day=cron_time.day,
        month=cron_time.month,
        sec=cron_time.second,
    )


# Prepare a cronjob that should start test_timeout/2 seconds from the application start
cron_time = datetime.datetime.now() + datetime.timedelta(seconds=test_timeout / 2)


@cron(make_cron_expr(cron_time))
def cron_test(**_):
    cron_queue.put('cron_test')


# Prepare another cronjob that should start 1hr + test_timeout/2 seconds from the application start
cron_time = datetime.datetime.now() + datetime.timedelta(
    hours=1, seconds=test_timeout / 2
)


@cron(make_cron_expr(cron_time))
def cron_1hr_test(**_):
    cron_queue.put('cron_1hr_test')
