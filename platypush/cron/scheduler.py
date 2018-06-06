import datetime
import logging
import re
import time

from threading import Thread

from platypush.event.hook import EventAction

logger = logging.getLogger(__name__)


class Cronjob(Thread):
    def __init__(self, name, cron_expression, actions, *args, **kwargs):
        super().__init__()
        self.cron_expression = cron_expression
        self.name = name
        self.actions = []

        for action in actions:
            self.actions.append(EventAction.build(action))


    def run(self):
        logger.info('Running cronjob {}'.format(self.name))
        response = None
        context = {}

        for action in self.actions:
            response = action.execute(async=False, **context)
            logger.info('Response from cronjob {}: {}'.format(self.name, response))


    def should_run(self):
        units = ('minute', 'hour', 'day', 'month', 'year')
        now = datetime.datetime.fromtimestamp(time.time())
        cron_units = re.split('\s+', self.cron_expression)

        for i in range(0, len(units)):
            unit = units[i]
            now_unit = getattr(now, unit)
            cron_unit = cron_units[i].replace('*', str(now_unit))
            m = re.match('(\d+)(/(\d+))?', cron_unit)

            if m.group(3):
                if int(m.group(1)) % int(m.group(3)):
                    return False
            elif m:
                if int(m.group(1)) != now_unit:
                    return False
            else:
                raise RuntimeError('Invalid cron expression for job {}: {}'.
                                   format(self.name, self.cron_expression))

        return True


class CronScheduler(Thread):
    def __init__(self, jobs, *args, **kwargs):
        super().__init__()
        self.jobs_config = jobs
        logger.info('Cron scheduler initialized with {} jobs'
                     .format(len(self.jobs_config.keys())))


    @classmethod
    def _build_job(cls, name, config):
        if isinstance(config, dict):
            job = Cronjob(name=name, cron_expression=config['cron_expression'],
                          actions=config['actions'])

        assert isinstance(job, Cronjob)
        return job


    def run(self):
        logger.info('Running cron scheduler')

        while True:
            for (job_name, job_config) in self.jobs_config.items():
                job = self._build_job(name=job_name, config=job_config)
                if job.should_run():
                    job.start()

            time.sleep(60)


# vim:sw=4:ts=4:et:

