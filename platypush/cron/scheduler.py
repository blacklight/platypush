import datetime
import enum
import logging
import threading

import croniter
from dateutil.tz import gettz

from platypush.procedure import Procedure
from platypush.utils import is_functional_cron, set_thread_name

logger = logging.getLogger('platypush:cron')


def get_now() -> datetime.datetime:
    """
    :return: A timezone-aware representation of `now`
    """
    return datetime.datetime.now().replace(
        tzinfo=gettz()  # lgtm [py/call-to-non-callable]
    )


class CronjobState(enum.IntEnum):
    IDLE = 0
    WAIT = 1
    RUNNING = 2
    DONE = 3
    ERROR = 4


class CronjobEvent(enum.IntEnum):
    NONE = 0
    STOP = 1
    TIME_SYNC = 2


class Cronjob(threading.Thread):
    def __init__(self, name, cron_expression, actions):
        super().__init__()
        self.cron_expression = cron_expression
        self.name = name
        self.state = CronjobState.IDLE
        self._event = threading.Event()
        self._event_type = CronjobEvent.NONE
        self._event_lock = threading.RLock()

        if isinstance(actions, (list, dict)):
            self.actions = Procedure.build(
                name=name + '__Cron', _async=False, requests=actions
            )
        else:
            self.actions = actions

    def notify(self, event: CronjobEvent):
        with self._event_lock:
            self._event_type = event
            self._event.set()

    def run(self):
        set_thread_name(f'cron:{self.name}')
        self.wait()
        if self.should_stop():
            return

        self.state = CronjobState.RUNNING

        try:
            logger.info('Running cronjob {}'.format(self.name))
            context = {}

            if isinstance(self.actions, Procedure):
                response = self.actions.execute(_async=False, **context)
            else:
                response = self.actions(**context)

            logger.info('Response from cronjob {}: {}'.format(self.name, response))
            self.state = CronjobState.DONE
        except Exception as e:
            logger.exception(e)
            self.state = CronjobState.ERROR

    def wait(self):
        with self._event_lock:
            self.state = CronjobState.WAIT
            self._event.clear()
            self._event_type = CronjobEvent.TIME_SYNC

        while self._event_type == CronjobEvent.TIME_SYNC:
            now = get_now()
            self._event_type = CronjobEvent.NONE
            cron = croniter.croniter(self.cron_expression, now)
            next_run = cron.get_next(datetime.datetime)
            self._event.wait(max(0, (next_run - now).total_seconds()))

    def stop(self):
        self._event_type = CronjobEvent.STOP
        self._event.set()

    def should_stop(self):
        return self._event_type == CronjobEvent.STOP


class CronScheduler(threading.Thread):
    def __init__(self, jobs, poll_seconds: float = 0.5):
        super().__init__()
        self.jobs_config = jobs
        self._jobs = {}
        self._poll_seconds = max(1e-3, poll_seconds)
        self._should_stop = threading.Event()
        logger.info(
            'Cron scheduler initialized with {} jobs'.format(
                len(self.jobs_config.keys())
            )
        )

    def _get_job(self, name, config):
        job = self._jobs.get(name)
        if job and job.state not in [CronjobState.DONE, CronjobState.ERROR]:
            return job

        if isinstance(config, dict):
            self._jobs[name] = Cronjob(
                name=name,
                cron_expression=config['cron_expression'],
                actions=config['actions'],
            )
        elif is_functional_cron(config):
            self._jobs[name] = Cronjob(
                name=name, cron_expression=config.cron_expression, actions=config
            )
        else:
            raise AssertionError(
                'Expected type dict or function for cron {}, got {}'.format(
                    name, type(config)
                )
            )

        return self._jobs[name]

    def stop(self):
        for job in self._jobs.values():
            job.stop()
        self._should_stop.set()

    def should_stop(self):
        return self._should_stop.is_set()

    def run(self):
        logger.info('Running cron scheduler')

        while not self.should_stop():
            for (job_name, job_config) in self.jobs_config.items():
                job = self._get_job(name=job_name, config=job_config)
                if job.state == CronjobState.IDLE:
                    try:
                        job.start()
                    except Exception as e:
                        logger.warning(f'Could not start cronjob {job_name}: {e}')

            t_before_wait = get_now().timestamp()
            self._should_stop.wait(timeout=self._poll_seconds)
            t_after_wait = get_now().timestamp()
            time_drift = abs(t_after_wait - t_before_wait) - self._poll_seconds

            if not self.should_stop() and time_drift > 1:
                # If the system clock has been adjusted by more than one second
                # (e.g. because of DST change or NTP sync) then ensure that the
                # registered cronjobs are synchronized with the new datetime
                logger.info(
                    'System clock drift detected: %f secs. Synchronizing the cronjobs',
                    time_drift,
                )

                for job in self._jobs.values():
                    job.notify(CronjobEvent.TIME_SYNC)

        logger.info('Terminating cron scheduler')


# vim:sw=4:ts=4:et:
