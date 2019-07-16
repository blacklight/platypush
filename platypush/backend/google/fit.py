import datetime
import time

from platypush.backend import Backend
from platypush.context import get_plugin
from platypush.message.event.google.fit import GoogleFitEvent
from platypush.utils import camel_case_to_snake_case


class GoogleFitBackend(Backend):
    """
    This backend will listen for new Google Fit events (e.g. new weight/height
    measurements, new fitness activities etc.) on the specified data streams and
    fire an event upon new data.

    Triggers:

        * :class:`platypush.message.event.google.fit.GoogleFitEvent` when a new
            data point is received on one of the registered streams.

    Requires:

        * The **google.fit** plugin
            (:class:`platypush.plugins.google.fit.GoogleFitPlugin`) enabled.
        * The **db** plugin (:class:`platypush.plugins.db`) configured
    """

    _default_poll_seconds = 60
    _default_user_id = 'me'
    _last_timestamp_varname = '_GOOGLE_FIT_LAST_TIMESTAMP_'

    def __init__(self, data_sources, user_id=_default_user_id,
                 poll_seconds=_default_poll_seconds, *args, **kwargs):
        """
        :param data_sources: Google Fit data source IDs to monitor. You can
            get a list of the available data sources through the
            :meth:`platypush.plugins.google.fit.get_data_sources` action
        :type data_sources: list[str]

        :param user_id: Google user ID to track (default: 'me')
        :type user_id: str

        :param poll_seconds: How often the backend will query the data sources
            for new data points (default: 60 seconds)
        :type poll_seconds: float
        """

        super().__init__(*args, **kwargs)

        self.data_sources = data_sources
        self.user_id = user_id
        self.poll_seconds = poll_seconds

    def run(self):
        super().run()
        self.logger.info('Started Google Fit backend on data sources {}'.format(
            self.data_sources))

        while not self.should_stop():
            try:
                for data_source in self.data_sources:
                    varname = self._last_timestamp_varname + data_source
                    last_timestamp = float(get_plugin('variable').
                                           get(varname).output.get(varname) or 0)

                    new_last_timestamp = last_timestamp
                    self.logger.info('Processing new entries from data source {}, last timestamp: {}'.
                                     format(data_source,
                                            str(datetime.datetime.fromtimestamp(last_timestamp))))

                    data_points = get_plugin('google.fit').get_data(
                        user_id=self.user_id, data_source_id=data_source).output
                    new_data_points = 0

                    for dp in data_points:
                        dp_time = dp.pop('startTime', 0)
                        if 'dataSourceId' in dp:
                            del dp['dataSourceId']

                        if dp_time > last_timestamp:
                            self.bus.post(GoogleFitEvent(
                                user_id=self.user_id, data_source_id=data_source,
                                data_type=dp.pop('dataTypeName'),
                                start_time=dp_time,
                                end_time=dp.pop('endTime'),
                                modified_time=dp.pop('modifiedTime'),
                                values=dp.pop('values'),
                                **{camel_case_to_snake_case(k): v
                                    for k, v in dp.items()}
                            ))

                            new_data_points += 1

                        new_last_timestamp = max(dp_time, new_last_timestamp)

                    last_timestamp = new_last_timestamp
                    self.logger.info('Got {} new entries from data source {}, last timestamp: {}'.
                                     format(new_data_points, data_source,
                                            str(datetime.datetime.fromtimestamp(last_timestamp))))

                    get_plugin('variable').set(**{varname: last_timestamp})
            except Exception as e:
                self.logger.warning('Exception while processing Fit data')
                self.logger.exception(e)
                continue

            time.sleep(self.poll_seconds)


# vim:sw=4:ts=4:et:
